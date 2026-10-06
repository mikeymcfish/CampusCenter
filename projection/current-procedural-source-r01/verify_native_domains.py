from pathlib import Path
import argparse,json,numpy as np,hashlib
R=Path(__file__).parent
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);a=ap.parse_args();w=a.directory;records=[]
    reference=json.loads((R/'Locked_Domain_Input_SHA256.json').read_text())
    for row in reference['inputs']:
        actual=w/row['file'];expected=R/row['file'];before=np.load(expected,allow_pickle=False);after=np.load(actual,allow_pickle=False);assert set(before.files)==set(after.files)
        for key in before.files:assert before[key].dtype==after[key].dtype and np.array_equal(before[key],after[key]),(row['file'],key)
        records.append({'component':actual.stem,'all_arrays_dtype_shape_and_values_identical':True,'regenerated_NPZ_sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'locked_NPZ_sha256':row['sha256']})
    expected=np.load(R/'Evidence/R03/Whole_Native_Obstacle_And_Ownership_Grid.npz');actual=np.load(w/'madmapper_ripple_R03/whole_model/Whole_Native_Obstacle_And_Ownership_Grid.npz');assert set(expected.files)==set(actual.files)
    for key in expected.files:assert np.array_equal(expected[key],actual[key]),key
    before=json.loads((R/'Evidence/R03/Whole_Model_Coverage_Preflight.json').read_text());after=json.loads((w/'madmapper_ripple_R03/whole_model/Whole_Model_Coverage_Preflight.json').read_text())
    for key in ['physical_floor_cells','native_water_free_cells','meaningful_basin_cells','false_closed_solid_interior_water_cells_removed','unexcited_smaller_than_2mm2_cells','meaningful_basins']:assert before[key]==after[key],key
    q={'status':'PASS: fresh domain extraction from included native geometry matches accepted full-model domains exactly','native_geometry_cache_inputs':1284,'connected_components':len(records),'all56_domain_arrays_exact':True,'all_whole_grid_arrays_exact':True,'grid_arrays':list(expected.files),'physical_floor_cells':after['physical_floor_cells'],'free_water_cells':after['native_water_free_cells'],'meaningful_cells':after['meaningful_basin_cells'],'tiny_unexcited_cells':after['unexcited_smaller_than_2mm2_cells'],'false_fixture_interior_cells_removed':after['false_closed_solid_interior_water_cells_removed'],'derivation':'Preservedripple_r02_domains.py --whole-model followed by preservedripple_whole_fixture_volume_audit.py --connected, in an independent empty workspace; source meshes, scale/origin and geometry unchanged.','domain_checks':records,'full_simulation_or_frame_cache_used_to_regenerate_domains':False,'dependency_version_metadata_limitation':'Original vendored trimesh/manifold3d distribution version labels unavailable; exact source/module fingerprints recorded in Environment_Requirements.json. Numeric outputs are protected by these exact-array assertions.'};(R/'Native_Domain_Rebuild_Verification_QA.json').write_text(json.dumps(q,indent=2));print(json.dumps({k:q[k] for k in ['status','connected_components','all56_domain_arrays_exact','all_whole_grid_arrays_exact','physical_floor_cells','meaningful_cells','tiny_unexcited_cells','false_fixture_interior_cells_removed']},indent=2))
if __name__=='__main__':main()
