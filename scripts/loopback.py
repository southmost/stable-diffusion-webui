import numpy as np
from tqdm import trange

import modules.scripts as scripts
import gradio as gr

from modules import processing, shared, sd_samplers, images
from modules.processing import Processed
from modules.sd_samplers import samplers
from modules.shared import opts, cmd_opts, state

class Script(scripts.Script):
    def title(self):
        return "Loopback"

    def show(self, is_img2img):
        return is_img2img

    def ui(self, is_img2img):
        loops = gr.Slider(minimum=1, maximum=32, step=1, label='Loops', value=8)
        denoising_strength_change_factor = gr.Slider(minimum=0.9, maximum=1.1, step=0.01, label='Denoising strength change factor', value=1)

        return [loops, denoising_strength_change_factor]

    def run(self, p, loops, denoising_strength_change_factor):
        processing.fix_seed(p)
        batch_count = p.n_iter # number of images to be generated
        p.extra_generation_params = {
            "Denoising strength change factor": denoising_strength_change_factor,
        }

        p.batch_size = 1 # number of images to be generated in one batch
        p.n_iter = 1 # number of images to be generated

        output_images, info = None, None
        initial_seed = None # seed for the first image
        initial_info = None

        grids = [] # list of grids
        all_images = [] # list of all images
        state.job_count = loops * batch_count # total number of images to be generated

        initial_color_corrections = [processing.setup_color_correction(p.init_images[0])]

        for n in range(batch_count): # for each batch
            history = [] # list of images in the batch

            for i in range(loops):
                p.n_iter = 1 # number of images to be generated in one batch
                p.batch_size = 1 # number of images to be generated in one batch
                p.do_not_save_grid = True # do not save grid

                if opts.img2img_color_correction:
                    p.color_corrections = initial_color_corrections

                state.job = f"Iteration {i + 1}/{loops}, batch {n + 1}/{batch_count}" # print the current iteration and batch

                processed = processing.process_images(p) # generate image

                if initial_seed is None:
                    initial_seed = processed.seed # seed for the first image
                    initial_info = processed.info

                init_img = processed.images[0]

                p.init_images = [init_img] # set the image to be generated as the previous image
                p.seed = processed.seed + 1 # set the seed for the next image
                p.denoising_strength = min(max(p.denoising_strength * denoising_strength_change_factor, 0.1), 1) # change the denoising strength
                history.append(processed.images[0]) # add the image to the list of images in the batch

            grid = images.image_grid(history, rows=1) # create a grid of images in the batch
            if opts.grid_save:
                images.save_image(grid, p.outpath_grids, "grid", initial_seed, p.prompt, opts.grid_format, info=info, short_filename=not opts.grid_extended_filename, grid=True, p=p)

            grids.append(grid) # add the grid to the list of grids
            all_images += history # add the images in the batch to the list of all images

        if opts.return_grid:
            all_images = grids + all_images # add the grids to the list of all images

        processed = Processed(p, all_images, initial_seed, initial_info)

        return processed
