"""Bounded synthetic experiment, incremental evidence and independent verification."""
import argparse
import hashlib
import importlib.metadata
import itertools
import json
import platform
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from threadpoolctl import threadpool_info, threadpool_limits
from .core import initialize, kmeans, bisect, _integer

ROOT = Path(__file__).resolve().parents[1]
CASES = ('separated', 'overlap', 'anisotropic')
METHODS = ('random', 'plus', 'bisect')


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def generate(case, seed, n):
    if case not in CASES:
        raise ValueError('Unknown generated case')
    _integer(seed, 'dataset seed', 0, 2**32-1)
    _integer(n, 'n', 6, 2000)
    if n % 3:
        raise ValueError('n must be divisible by three')
    rng = np.random.default_rng(seed)
    centers = np.array([[-4., -1.], [0., 4.], [4., -1.]])
    y = np.repeat(np.arange(3), n//3)
    scale = {'separated': .65, 'overlap': 2.1, 'anisotropic': 1.15}[case]
    x = centers[y] + rng.normal(size=(n, 2)) * scale
    if case == 'anisotropic':
        x = x @ np.array([[1., .8], [0., .13]])
    order = rng.permutation(n)
    return np.ascontiguousarray(x[order]), y[order]


def _config(config):
    expected = {'cases','dataset_seeds','init_seeds','methods','n','k','max_iter','order_seed'}
    if not isinstance(config, dict) or set(config) != expected:
        raise ValueError('Configuration fields must match the documented schema')
    c = json.loads(json.dumps(config, allow_nan=False))
    for name, allowed in [('cases', CASES), ('methods', METHODS)]:
        if not isinstance(c[name], list) or not c[name] or any(v not in allowed for v in c[name]) or len(c[name]) != len(set(c[name])):
            raise ValueError(f'{name} must contain unique supported names')
    for name in ('dataset_seeds', 'init_seeds'):
        if not isinstance(c[name], list) or not 1 <= len(c[name]) <= 10:
            raise ValueError(f'{name} must have 1..10 seeds')
        for seed in c[name]: _integer(seed, name, 0, 2**32-1)
        if len(set(c[name])) != len(c[name]): raise ValueError('Seeds must be unique')
    _integer(c['k'], 'k', 3, 3)
    _integer(c['n'], 'n', 6, 2000)
    if c['n'] % 3: raise ValueError('n must be divisible by three')
    _integer(c['max_iter'], 'max_iter', 1, 10000)
    _integer(c['order_seed'], 'order_seed', 0, 2**32-1)
    return c


def repository_state(root):
    root = Path(root).resolve()
    top = subprocess.run(['git','-C',str(root),'rev-parse','--show-toplevel'],capture_output=True,text=True)
    if top.returncode or Path(top.stdout.strip()).resolve() != root:
        raise ValueError('Evidence requires this project as the repository root')
    commit = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    status = subprocess.check_output(['git','-C',str(root),'status','--porcelain'],text=True)
    return {'commit':commit,'working_tree_clean':not bool(status)}


def _sources():
    files = sorted((ROOT/'clustering_study').glob('*.py')) + [ROOT/'requirements.txt']
    return {str(p.relative_to(ROOT)):_digest(p.read_bytes()) for p in files}


def _write(output, record):
    temp = output/'study.json.tmp'
    temp.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    temp.replace(output/'study.json')


def _metrics(x, y, labels, centers):
    residual = x-centers[labels]
    occupied = len(np.unique(labels))
    return {'inertia':float(np.einsum('ij,ij->',residual,residual)),
            'ari':float(adjusted_rand_score(y,labels)),
            'silhouette':float(silhouette_score(x,labels)) if 1 < occupied < len(x) else None,
            'effective_k':occupied}


def _fit(x, method, seed, config):
    if method == 'bisect':
        return bisect(x, config['k'], seed=seed, max_iter=config['max_iter'])
    return kmeans(x, config['k'], seed=seed, init=method, max_iter=config['max_iter'])


def run_study(config, output):
    config = _config(config)
    provenance = repository_state(ROOT)
    source = _sources()
    output = Path(output)
    output.mkdir(parents=True,exist_ok=False)
    record = {'schema':1, 'status':'incomplete', 'created_utc':datetime.now(timezone.utc).isoformat(),
              'config':config,'config_sha256':_digest(_canonical(config)), 'source_sha256':source,
              **provenance, 'environment':{'system':platform.system(), 'os_release':platform.release(),
              'machine':platform.machine(),'processor':platform.processor(), 'python':platform.python_version(),
              'packages':{name:importlib.metadata.version(name) for name in ('numpy','scipy','scikit-learn','matplotlib','threadpoolctl')}},
              'datasets':[], 'runs':[]}
    _write(output,record)
    try:
        with threadpool_limits(limits=1):
            record['environment']['threadpools'] = [{k:v for k,v in item.items() if k!='filepath'} for item in threadpool_info()]
            data = {}
            for case, seed in itertools.product(config['cases'],config['dataset_seeds']):
                x,y = generate(case,seed,config['n'])
                filename=f'{case}-{seed}.npz'
                np.savez(output/filename,x=x,y=y)
                record['datasets'].append({'case':case,'seed':seed,'file':filename,'sha256':_digest((output/filename).read_bytes()),
                    'array_sha256':_digest(x.astype('<f8').tobytes()+y.astype('<i8').tobytes())})
                data[case,seed]=(x,y)
            warm_x,_ = generate('separated',0,60)
            for method in config['methods']: _fit(warm_x,method,0,config)
            schedule=list(itertools.product(config['cases'],config['dataset_seeds'],config['init_seeds'],config['methods']))
            np.random.default_rng(config['order_seed']).shuffle(schedule)
            for case,ds,seed,method in schedule:
                x,y=data[case,ds]
                start=time.perf_counter()
                result=_fit(x,method,seed,config)
                elapsed=time.perf_counter()-start
                entry={'case':case,'dataset_seed':ds,'init_seed':seed,'method':method,
                       'centers':result.centers.tolist(),'labels':result.labels.tolist(),
                       'initial_centers':None if result.initial_centers is None else result.initial_centers.tolist(),
                       'n_iter':result.n_iter,'converged':result.converged,'relocations':result.relocations,
                       'objective_history':result.history,'fit_seconds':elapsed,
                       **_metrics(x,y,result.labels,result.centers)}
                if method != 'bisect':
                    ref=KMeans(n_clusters=config['k'],init=result.initial_centers,n_init=1,tol=0,
                               max_iter=config['max_iter'],algorithm='lloyd').fit(x)
                    entry['reference']={'inertia':float(ref.inertia_),'labels':ref.labels_.tolist(),
                        'centers':ref.cluster_centers_.tolist(),'n_iter':int(ref.n_iter_),
                        'agreement_ari':float(adjusted_rand_score(result.labels,ref.labels_))}
                record['runs'].append(entry)
                _write(output,record)
            if _sources()!=source: raise ValueError('Source changed during experiment')
            record['status']='complete'
            _write(output,record)
            verify_run(output)
    except BaseException as error:
        record['status']='failed'
        record['error']=type(error).__name__+': '+str(error)
        _write(output,record)
        raise
    return record


def verify_run(output):
    """Recompute data identity, fit invariants and metrics; never trust stored scores."""
    output=Path(output)
    record=json.loads((output/'study.json').read_text())
    if record.get('schema')!=1 or record.get('status')!='complete':
        raise ValueError('Only complete schema-1 records can be plotted')
    c=_config(record['config'])
    if record['config_sha256']!=_digest(_canonical(c)):raise ValueError('Configuration hash mismatch')
    if not record.get('source_sha256'):raise ValueError('Missing source fingerprints')
    for name,sha in record['source_sha256'].items():
        if name not in _sources() or _sources()[name]!=sha:raise ValueError('Source fingerprint mismatch')
    expected_datasets=set(itertools.product(c['cases'],c['dataset_seeds']))
    data={}
    for item in record['datasets']:
        key=(item['case'],item['seed']);filename=f'{key[0]}-{key[1]}.npz'
        if key not in expected_datasets or key in data or item['file']!=filename:raise ValueError('Unexpected dataset')
        path=output/filename
        if _digest(path.read_bytes())!=item['sha256']:raise ValueError('Dataset file hash mismatch')
        with np.load(path,allow_pickle=False) as saved:x,y=saved['x'],saved['y']
        expected_x,expected_y=generate(*key,c['n'])
        if not np.array_equal(x,expected_x) or not np.array_equal(y,expected_y):raise ValueError('Generated data mismatch')
        if _digest(x.astype('<f8').tobytes()+y.astype('<i8').tobytes())!=item['array_sha256']:raise ValueError('Array hash mismatch')
        data[key]=(x,y)
    if set(data)!=expected_datasets:raise ValueError('Missing dataset')
    expected=set(itertools.product(c['cases'],c['dataset_seeds'],c['init_seeds'],c['methods']))
    seen=set()
    with threadpool_limits(limits=1):
        for run in record['runs']:
            key=(run['case'],run['dataset_seed'],run['init_seed'],run['method'])
            if key not in expected or key in seen:raise ValueError('Unexpected or duplicated fit')
            seen.add(key)
            x,y=data[key[:2]]
            labels=np.asarray(run['labels']);centers=np.asarray(run['centers'],dtype=float)
            if labels.shape!=(len(x),) or labels.dtype.kind not in 'iu' or labels.min()<0 or labels.max()>=c['k']:
                raise ValueError('Invalid labels')
            if centers.shape!=(c['k'],2) or not np.isfinite(centers).all():raise ValueError('Invalid centers')
            if type(run['converged']) is not bool:raise ValueError('Invalid convergence status')
            if not np.isfinite(run['fit_seconds']) or run['fit_seconds']<0:raise ValueError('Invalid timing')
            for metric,value in _metrics(x,y,labels,centers).items():
                if value is None:
                    if run[metric] is not None:raise ValueError('Undefined metric reported as numeric')
                elif not np.isclose(value,run[metric],rtol=1e-11,atol=1e-12):raise ValueError(f'{metric} mismatch')
            if key[3]!='bisect':
                nearest=((x[:,None]-centers)**2).sum(axis=2).argmin(axis=1)
                if not np.array_equal(labels,nearest):raise ValueError('Labels not nearest to centers')
                init=initialize(x,c['k'],key[2],key[3])
                if not np.array_equal(init,np.asarray(run['initial_centers'])):raise ValueError('Initialization mismatch')
                ref=run['reference'];rc=np.asarray(ref['centers']);rl=np.asarray(ref['labels'])
                if rc.shape!=(c['k'],2) or rl.shape!=(len(x),) or rl.dtype.kind not in 'iu' or rl.min()<0 or rl.max()>=c['k']:
                    raise ValueError('Invalid reference output')
                inertia=float(((x-rc[rl])**2).sum())
                if not np.isclose(inertia,ref['inertia'],rtol=1e-11):raise ValueError('Reference inertia mismatch')
                if adjusted_rand_score(labels,rl)!=ref['agreement_ari']:raise ValueError('Reference ARI mismatch')
            if run['converged'] or key[3]=='bisect':
                for j in range(c['k']):
                    if not np.any(labels==j) or not np.allclose(centers[j],x[labels==j].mean(axis=0),rtol=1e-11,atol=1e-12):
                        raise ValueError('Occupied-centroid mean invariant failed')
    if seen!=expected:raise ValueError('Missing fit')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['run','verify'])
    parser.add_argument('output',type=Path)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/study.json')
    args=parser.parse_args()
    if args.command=='run':
        record=run_study(json.loads(args.config.read_text()),args.output)
    else:record=verify_run(args.output)
    print(f"{record['status']}: {len(record['runs'])} fits verified")


if __name__=='__main__':main()
