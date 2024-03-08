import os
import cv2
import logging
import numpy as np
from math import ceil, floor
from matplotlib import pyplot as plt

import cmaas_utils.io as io
from cmaas_utils.types import CMASS_Map, CMASS_Legend, CMASS_Feature

log = logging.getLogger('DARPA_CMAAS')

# viz georef

# viz layouts

# ocr text viz?
# Save an image of a predicted contour
def saveContour(image, contour, filename, pad=100):
    x, y, w, h = cv2.boundingRect(contour)
    x1, y1 = max(x-pad,0), max(y-pad,0)
    x2, y2 = min(x+w+pad, image.shape[1]), min(y+h+pad, image.shape[0])
    cv2.imwrite(filename, image[y1:y2, x1:x2, :])

# viz map unit labels
# Save Legend preview
def save_legend_preview(map_data, feedback_dir, legend_feedback_mode):
    legend_images = {}
    for label, feature in map_data.legend.features.items():
        min_pt, max_pt = boundingBox(feature.contour) # Need this as points order can be reverse or could have quad
        legend_images[feature.name] = map_data.image[:,min_pt[1]:max_pt[1], min_pt[0]:max_pt[0]]
        if feedback_dir:
            os.makedirs(os.path.join(feedback_dir, map_data.name), exist_ok=True)
            if legend_feedback_mode == 'individual_images':
                legend_save_path = os.path.join(feedback_dir, map_data.name, 'lgd_' + map_data.name + '_' + feature.name + '.tif')
                io.saveGeoTiff(legend_save_path, legend_images[feature.name], None, None)
    if feedback_dir and len(legend_images) > 0:
        os.makedirs(os.path.join(feedback_dir, map_data.name), exist_ok=True)
        if legend_feedback_mode == 'single_image':
            cols = 4
            rows = ceil(len(legend_images)/cols)
            fig, ax = plt.subplots(rows, cols, figsize=(16,16))
            ax = ax.reshape(rows, cols) # Force 2d shape if less the 4 items
            for r,c in np.ndindex(ax.shape):
                ax[r][c].axis('off')
            for i, label in enumerate(legend_images):
                row, col  = floor(i/cols), i%cols
                ax[row][col].set_title(label)
                ax[row][col].imshow(legend_images[label].transpose(1,2,0))
            legend_save_path = os.path.join(feedback_dir, map_data.name, map_data.name + '_labels'  + '.png')
            fig.savefig(legend_save_path)

# viz map segmentations

# viz map points

# viz map lines?

# put some scoring vizulations in here?