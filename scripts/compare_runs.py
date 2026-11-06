#!/usr/bin/env python3
"""Compare complete repeated experiments; measured times are intentionally excluded."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from clustering_study.experiment import verify_run


def compare_runs(first, second):
    a,b=verify_run(first),verify_run(second)
    if a['config']!=b['config'] or a['source_sha256']!=b['source_sha256']:
        raise ValueError('Experiment design or source differs')
    def numerical(record):
        inputs=sorted((d['case'],d['seed'],d['array_sha256']) for d in record['datasets'])
        fits=[{k:v for k,v in r.items() if k!='fit_seconds'} for r in record['runs']]
        fits.sort(key=lambda r:(r['case'],r['dataset_seed'],r['init_seed'],r['method']))
        return {'inputs':inputs,'fits':fits}
    x,y=numerical(a),numerical(b)
    if x!=y:raise ValueError('Numerical results differ')
    digest=hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    return {'numerically_identical_fits':len(a['runs']),'numerical_sha256':digest,
            'first_record_sha256':hashlib.sha256((Path(first)/'study.json').read_bytes()).hexdigest(),
            'second_record_sha256':hashlib.sha256((Path(second)/'study.json').read_bytes()).hexdigest(),
            'source_commit_first':a['commit'],'source_commit_second':b['commit'],
            'scope':'Exact inputs and numerical outputs. Timings, timestamps and environment metadata excluded.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first',type=Path);parser.add_argument('second',type=Path)
    args=parser.parse_args()
    print(json.dumps(compare_runs(args.first,args.second),indent=2))
