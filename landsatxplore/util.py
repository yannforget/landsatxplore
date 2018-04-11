"""Utility functions."""


def is_product_id(identifier):
    """Check if a given identifier is a product identifier
    as opposed to a legacy scene identifier.
    """
    return len(identifier) == 40


def guess_dataset(identifier):
    """Guess data set based on a scene identifier."""
    if is_product_id(identifier):
        sat = int(identifier[3])
    else:
        sat = int(identifier[2])
    datasets = {5: 'LANDSAT_TM_C1', 7: 'LANDSAT_ETM_C1', 8: 'LANDSAT_8_C1'}
    return datasets[sat]
