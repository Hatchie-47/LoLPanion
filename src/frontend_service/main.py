import common.lol_logging
import customtkinter as ctk
from controllers.main import Controller
from models.main import Model
from views.main import View
import logging

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('green')

if __name__ == '__main__':
    logging.info('Starting frontend service...')
    try:
        main_model = Model()
        main_view = View()
        main_controller = Controller(main_model, main_view)
        main_controller.start()
    except Exception as e:
        logging.critical(e, exc_info=True)
    finally:
        logging.info('Stopping frontend service...')
