import copy
import json
from pathlib import Path
import subprocess
import numpy as np
import pytest
from clustering_study.experiment import generate, run_study, verify_run, repository_state

CONFIG = {'cases':['separated','overlap','anisotropic'], 'dataset_seeds':[11], 'init_seeds':[101],
          'methods':['random','plus','bisect'], 'n':60, 'k':3, 'max_iter':300, 'order_seed':90210}


def test_generation_is_deterministic_balanced_and_geometry_changes():
    a,y = generate('separated',11,60)
    b,z = generate('separated',11,60)
    np.testing.assert_array_equal(a,b)
    np.testing.assert_array_equal(y,z)
    assert np.bincount(y).tolist() == [20,20,20]
    assert a.shape == (60,2) and np.isfinite(a).all()
    assert not np.array_equal(a,generate('overlap',11,60)[0])
    assert not np.array_equal(a,generate('separated',22,60)[0])


@pytest.mark.parametrize('args',[('unknown',11,60),('separated',-1,60),('separated',11,61),('separated',11,0)])
def test_generation_rejects_invalid_inputs(args):
    with pytest.raises(ValueError):generate(*args)


def test_complete_record_and_no_overwrite(tmp_path):
    output = tmp_path/'run'
    run_study(CONFIG,output)
    data = verify_run(output)
    assert data['status']=='complete' and len(data['runs'])==9
    assert all(r['converged'] and r['effective_k']==3 for r in data['runs'])
    assert all(r['reference']['agreement_ari']==1 for r in data['runs'] if r['method']!='bisect')
    before = (output/'study.json').read_bytes()
    with pytest.raises(FileExistsError):run_study(CONFIG,output)
    assert (output/'study.json').read_bytes()==before


@pytest.mark.parametrize('field,value',[('n',61),('k',True),('methods',['unknown']),('init_seeds',[1,1]),('max_iter',0)])
def test_bad_configuration_fails_before_output_created(tmp_path,field,value):
    cfg=copy.deepcopy(CONFIG);cfg[field]=value
    with pytest.raises(ValueError):run_study(cfg,tmp_path/'run')
    assert not (tmp_path/'run').exists()


@pytest.fixture
def saved(tmp_path):
    output=tmp_path/'run';run_study(CONFIG,output);return output


@pytest.mark.parametrize('change',['inertia','labels','metric','incomplete','missing_run','input','config'])
def test_verifier_rejects_corrupted_evidence(saved,change):
    p=saved/'study.json';d=json.loads(p.read_text())
    if change=='inertia': d['runs'][0]['inertia']+=1
    elif change=='labels': d['runs'][0]['labels'][0]=99
    elif change=='metric': d['runs'][0]['ari']=-1
    elif change=='incomplete':d['status']='incomplete'
    elif change=='missing_run':d['runs'].pop()
    elif change=='config':d['config']['init_seeds']=[999]
    else:
        path=saved/d['datasets'][0]['file'];path.write_bytes(b'broken')
    p.write_text(json.dumps(d))
    with pytest.raises((ValueError,AssertionError)):verify_run(saved)


def test_enclosing_git_is_not_project_provenance(tmp_path):
    subprocess.run(['git','init',str(tmp_path)],check=True,capture_output=True)
    child=tmp_path/'child';child.mkdir()
    with pytest.raises(ValueError,match='repository root'):repository_state(child)


@pytest.mark.parametrize('change',['source_subset','iterations','relocations','history','convergence','reference'])
def test_replay_rejects_fabricated_algorithm_metadata(saved,change):
    p=saved/'study.json';d=json.loads(p.read_text());r=d['runs'][0]
    if change=='source_subset':d['source_sha256']={'requirements.txt':d['source_sha256']['requirements.txt']}
    elif change=='iterations':r['n_iter']=-999
    elif change=='relocations':r['relocations']='invented'
    elif change=='history':r['objective_history']=[-100,1e100]
    elif change=='convergence':r['converged']=not r['converged']
    else:
        r=next(x for x in d['runs'] if x['method']!='bisect')
        r['reference']['n_iter']=-2
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError):verify_run(saved)


def test_failed_final_validation_never_observes_complete_record(tmp_path,monkeypatch):
    from clustering_study import experiment
    output=tmp_path/'interrupted'
    def interrupted_verification(path,**kwargs):
        assert json.loads((Path(path)/'study.json').read_text())['status']=='incomplete'
        raise InterruptedError('simulated interruption at validation boundary')
    monkeypatch.setattr(experiment,'verify_run',interrupted_verification)
    with pytest.raises(InterruptedError):run_study(CONFIG,output)
    saved=json.loads((output/'study.json').read_text())
    assert saved['status']=='failed' and len(saved['runs'])==9


def test_compare_repeated_numerics_and_reject_changed_design(tmp_path):
    from scripts.compare_runs import compare_runs
    a=tmp_path/'a';b=tmp_path/'b';c=tmp_path/'c'
    run_study(CONFIG,a);run_study(CONFIG,b)
    assert compare_runs(a,b)['numerically_identical_fits']==9
    changed=copy.deepcopy(CONFIG);changed['init_seeds']=[202]
    run_study(changed,c)
    with pytest.raises(ValueError):compare_runs(a,c)
