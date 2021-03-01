"""Utility functions."""

from landsatxplore.errors import LandsatxploreError


def _is_landsat_product_id(id):
    return len(id) == 40 and id.startswith("L")


def _is_landsat_scene_id(id):
    return len(id) == 21 and id.startswith("L")


def _is_sentinel_display_id(id):
    return len(id) == 34 and id.startswith("L")


def _is_sentinel_entity_id(id):
    return len(id) == 8 and id.isdecimal()


def is_display_id(id):
    return _is_landsat_product_id(id) or _is_sentinel_display_id(id)


def is_entity_id(id):
    return _is_landsat_scene_id(id) or _is_sentinel_entity_id(id)


def is_product_id(identifier):
    """Check if a given identifier is a product identifier
    as opposed to a legacy scene identifier.
    """
    return len(identifier) == 40 and identifier.startswith("L")


def parse_product_id(product_id):
    """Retrieve information from a product identifier.

    Parameters
    ----------
    product_id : str
        Landsat product identifier (also referred as Display ID).

    Returns
    -------
    meta : dict
        Retrieved information.
    """
    elements = product_id.split("_")
    return {
        "product_id": product_id,
        "sensor": elements[0][1],
        "satellite": elements[0][2:4],
        "processing_level": elements[1],
        "satellite_orbits": elements[2],
        "acquisition_date": elements[3],
        "processing_date": elements[4],
        "collection_number": elements[5],
        "collection_category": elements[6],
    }


def parse_scene_id(scene_id):
    """Retrieve information from a scene identifier.

    Parameters
    ----------
    scene_id : str
        Landsat scene identifier (also referred as Entity ID).

    Returns
    -------
    meta : dict
        Retrieved information.
    """
    return {
        "scene_id": scene_id,
        "sensor": scene_id[1],
        "satellite": scene_id[2],
        "path": scene_id[3:6],
        "row": scene_id[6:9],
        "year": scene_id[9:13],
        "julian_day": scene_id[13:16],
        "ground_station": scene_id[16:19],
        "archive_version": scene_id[19:21],
    }


def landsat_dataset(satellite, collection="c1", level="l1"):
    """Get landsat dataset name."""
    if satellite == 5:
        sensor = "tm"
    elif satellite == 7:
        sensor = "etm"
    elif satellite == 8 and collection == "c1":
        sensor = "8"
    elif satellite == 8 and collection == "c2":
        sensor = "ot"
    else:
        raise LandsatxploreError("Failed to guess dataset from identifier.")
    dataset = f"landsat_{sensor}_{collection}"
    if collection == "c2":
        dataset += f"_{level}"
    return dataset


def guess_dataset(identifier):
    """Guess data set based on a scene identifier."""
    # Landsat Product Identifier
    if _is_landsat_product_id(identifier):
        meta = parse_product_id(identifier)
        satellite = int(meta["satellite"])
        collection = "c" + meta["collection_number"][-1]
        level = meta["processing_level"][:2].lower()
        return landsat_dataset(satellite, collection, level)
    elif _is_landsat_scene_id(identifier):
        meta = parse_scene_id(identifier)
        satellite = int(meta["satellite"])
        return landsat_dataset(satellite)
    elif _is_sentinel_display_id(identifier) or _is_sentinel_entity_id(identifier):
        return "sentinel_2a"
    else:
        raise LandsatxploreError("Failed to guess dataset from identifier.")


def title_to_snake(src_string):
    """Convert title string to snake_case."""
    return src_string.lower().replace(" ", "_").replace("/", "-")


def camel_to_snake(src_string):
    """Convert camelCase string to snake_case."""
    dst_string = [src_string[0].lower()]
    for c in src_string[1:]:
        if c in ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            dst_string.append("_")
            dst_string.append(c.lower())
        else:
            dst_string.append(c)
    return "".join(dst_string)
