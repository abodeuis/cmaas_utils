import cv2
import numpy as np
from typing import List
from shapely.geometry import shape
from rasterio.features import shapes, sieve 
from .types import AreaBoundary, Legend, MapSegmentation, MapUnitType,  MapUnitSegmentation

def generate_poly_geometry(segmentation:MapSegmentation, legend:Legend, noise_threshold=10):
    """
    Generate vector polygon geometry for each map unit in the legend from the segmentation mask.

    Args:
        segmentation (MapSegmentation): The segmentation mask for the map.
        legend (Legend): The legend for the map.
        noise_threshold (int, optional): The number of pixels that can be considered noise. Defaults to 10.

    Returns:
        Legend: The legend with the polygon geometry added to each feature
    """
    legend_index = 1
    for feature in legend.features:
        if feature.type != MapUnitType.POLYGON:
            continue
        # Get mask of feature
        feature_mask = np.zeros_like(segmentation.image, dtype=np.uint8)
        feature_mask[segmentation.image == legend_index] = 1
        # Remove "noise" from mask by removing pixel groups smaller then the threshold
        sieve_img = sieve(feature_mask, noise_threshold, connectivity=4)
        # Convert mask to vector shapes
        shape_gen = shapes(sieve_img, connectivity=4)
        # Only use Filled pixels (1s) for shapes 
        geometries = [shape(geometry) for geometry, value in shape_gen if value == 1]
        # Add geometry to feature segmentation
        feature.segmentation = MapUnitSegmentation(provenance=segmentation.provenance, geometry=geometries, confidence=segmentation.confidence)
        legend_index += 1
    return legend

def generate_point_geometry(segmentation:MapSegmentation, legend:Legend):
    """
    Generate vector point geometry for each map unit in the legend from the segmentation mask.
    
    Args:
        segmentation (MapSegmentation): The segmentation mask for the map.
        legend (Legend): The legend for the map.
        
    Returns:
        Legend: The legend with the point geometry added to each feature
    """
    legend_index = 1
    for feature in legend.features:
        if feature.type != MapUnitType.POINT:
            continue
        # Get mask of feature
        feature_mask = np.zeros_like(segmentation.image, dtype=np.uint8)
        feature_mask[segmentation.image == legend_index] = 1
        # Get points from mask
        point_geometry = np.transpose(feature_mask.nonzero())
        # Convert geometry to List(List(List(float)))
        point_geometry = [[point] for point in point_geometry]
        feature.segmentation = MapUnitSegmentation(provenance=segmentation.provenance, geometry=point_geometry, confidence=segmentation.confidence)
        legend_index += 1
    return legend

def mask_and_crop(image, areas):
    """
    Mask and crop an image based on a list of areas.

    Args:
        image (np.array): The image to mask and crop, should be numpy array of shape (C,H,W)
        areas (List[AreaShape]): A list of areas to mask.

    Returns:
        np.array: The masked and cropped image.
        Tuple[int,int]: The x and y offset of the cropped image from the top left of the original. 
    """
    # Create a mask of the image
    t_img = image.transpose(1,2,0).copy()
    mask = np.zeros(t_img.shape[:2], dtype=np.uint8)
    for area in areas:
        cv2.fillPoly(mask, [np.array(area.geometry, dtype=np.int32)], 255)
    # Mask the image
    masked_img = cv2.bitwise_and(t_img, t_img, mask=mask)
    if len(masked_img.shape) == 2:
        masked_img = np.expand_dims(masked_img, axis=2)
    # Crop the image
    x, y, w, h = cv2.boundingRect(mask)
    cropped_img = masked_img[y:y+h, x:x+w]
    cropped_img = cropped_img.transpose(2,0,1)
    return cropped_img, (x,y)