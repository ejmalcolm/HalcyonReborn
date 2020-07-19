from files import get_file, save_file

def check_vision(viewer_uid, target_entity, target_region_xy):
    '''Checks if the viewer should be able to see the target'''
    # see if the viewer has anyone in the target region
    Regions = get_file('Regions.pickle')
    target_region = Regions[region_string_to_int(target_region_xy)]
    in_region = False
    for entity in target_region:
        if entity.owner_uid == viewer_uid:
            in_region = True
    if not in region:
        return "ERROR: NO FRIENDLY UNIT IN REGION"
    