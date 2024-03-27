from pynq import Overlay
from pynq.lib.video.common import VideoMode
import os
import xrfdc
import xrfclk
import time

# Import overlay specific drivers
import clocks

MAX_FS = 61.44e6

class Overlay(Overlay):
    """
    """
    
    def __init__(self, bitfile_name=None, init_rf_clks=True, **kwargs):
        """
        """
        
        # Generate default bitfile name
        if bitfile_name is None:
            this_dir = os.path.dirname(__file__)
            bitfile_name = os.path.join(this_dir, 'design_1_wrapper.bit')

        # Create Overlay
        super().__init__(bitfile_name, **kwargs)

        # Determine board and set PLL appropriately
        board = os.environ['BOARD']
        
        # Extract friendly dataconverter names
        if board == 'RFSoC4x2':
            self.adc_tile = self.rfdc.adc_tiles[2]
            self.adc_block = self.adc_tile.blocks[1]
        else:
            raise RuntimeError('Unknown error occurred.') # shouldn't get here
            
        # Start up LMX clock
        if init_rf_clks:
            clocks.set_custom_lmclks()
            
        self.configure_vdma()
        self.configure_adcs(sample_freq=4915.2, pll_freq=491.52, nyquist_zone=1, centre_freq=-2400)
        #self.axi_gpio.channel1.write(0x1, 0xF)
        
        
    def configure_vdma(self, height=1024, width=2048, bits_per_pixel=32):
        """
        """
        fps = MAX_FS / (height*width)
        mode = VideoMode(height=height, width=width, bits_per_pixel=bits_per_pixel, fps=fps)
        self.axi_vdma.readchannel.mode = mode
        #self.axi_vdma.readchannel.start()
        
        
    def configure_adcs(self, pll_freq=384.00, sample_freq=3840.00, nyquist_zone=1, centre_freq=-600):
        """
        """
        
        self.adc_tile.DynamicPLLConfig(1, pll_freq, sample_freq)
        self.adc_block.NyquistZone = nyquist_zone
        self.adc_block.MixerSettings = {
            'CoarseMixFreq'  : xrfdc.COARSE_MIX_BYPASS,
            'EventSource'    : xrfdc.EVNT_SRC_TILE,
            'FineMixerScale' : xrfdc.MIXER_SCALE_1P0,
            'Freq'           : centre_freq,
            'MixerMode'      : xrfdc.MIXER_MODE_R2C,
            'MixerType'      : xrfdc.MIXER_TYPE_FINE,
            'PhaseOffset'    : 0.0
        }
        self.adc_block.UpdateEvent(xrfdc.EVENT_MIXER)
        self.adc_tile.SetupFIFO(True)