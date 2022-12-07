# -------------------------------------------------------------------
# SeisClient
#
# Author: Liang Ding
# Email: myliang.ding@mail.utoronto.ca
# Data: Nov. 16th, 2022
# -------------------------------------------------------------------

import os
import io

from seisclient.db import dbBase
from seisgen.DSGTMgr import DSGTMgr
from seisgen.DDGFMgr import DDGFMgr

import requests
import pickle
import json

class SeisClientBase(dbBase):
    '''
    Request data  from SeisCloud.

    * Only SGT and DGF is requested from SeisCloud.
    * Greens function and synthetic waveform are calculated by using SeisGen.
    '''

    def __init__(self, db_url=None, db_port=None):
        super().__init__(db_url=db_url, db_port=db_port)

    def __check(self):
        '''Check input data'''
        pass

    def __request_model_info(self, model):
        '''Requst model parameters.'''
        if self.db_port is None:
            ip_addr = self.db_url
        else:
            ip_addr = '%s:%s' % (self.db_url, self.db_port,)

        request_cmd = '%s/models?' \
                      'model=%s&' \
                      % (ip_addr, str(model).upper())

        r = requests.get(request_cmd)
        if r.status_code == 200:
            try:
                buffer = io.BytesIO(r.content)
                info = json.load(buffer)
                return info
            except:
                raise ValueError
        else:
            raise ValueError


    def __request_db(self, model, station, origin, data_type):
        ''' Requst data form SeisCloud. '''

        if self.db_port is None:
            ip_addr = self.db_url
        else:
            ip_addr = '%s:%s' % (self.db_url, self.db_port,)

        request_cmd = '%s/request?' \
                      'model=%s&' \
                      'network=%s&' \
                      'station=%s&' \
                      'rlat=%.4f&' \
                      'rlon=%.4f&' \
                      'data_type=%s&' \
                      'slat=%.4f&' \
                      'slon=%.4f&' \
                      'sdepth_in_m=%d' \
                      % (ip_addr, str(model).upper(),
                         str(station.network).upper(), str(station.station).upper(),
                         station.latitude, station.longitude,
                         str(data_type).upper(),
                         origin.latitude, origin.longitude, origin.depth_in_m)

        # request SGT from remote database
        r = requests.get(request_cmd)
        if r.status_code == 200:
            try:
                buffer = io.BytesIO(r.content)
                # return SGT
                data = pickle.load(buffer)
                dt_gf = pickle.load(buffer)
                dt_stf = pickle.load(buffer)
                self.dt_gf = dt_gf
                self.dt_stf = dt_stf

                return data
            except:
                raise ValueError
        else:
            raise ValueError


    def __read_or_download(self, model, station, origin, save_dir, data_type):
        '''
        Read the data form either local folder or download from remote server.
        :param model:   The identifier (name) of 3D background model.
        :param station: An instance of the obspy AttribDict class. For example:
                        station = AttribDict({ 'latitude': 34.0210,
                                                'longitude': -118.287,
                                                'network': 'CI',
                                                'station': 'USC',
                                                'location': '',
                                                'id': 'USC'})

        :param origin:  An instance of the obspy AttribDict class. For example:
                        origin = Origin({'time': '2019-07-04T18:39:44.0000Z',
                                              'latitude': 35.601333,
                                              'longitude': -117.597,
                                              'depth_in_m': 2810.0,
                                              'id': 'evt11056825'})
        :param save_dir: The directory to store the downloaded data.
        :param data_type: Either 'SGT' or 'DGF'.
        :return:
        '''

        f_name = '%s.%s.%s.%.4f.%.4f.%.4f.%s.PKL' % (str(model).upper(),
                                                     station.network, station.station,
                                                     origin.latitude, origin.longitude,
                                                     origin.depth_in_m, data_type)

        # Check if the strain Green's Function (GF) is downloaded,
        # Read from the PKL file or re-download from SeisCloud.
        f_path = os.path.join(str(save_dir), str(f_name))
        b_save = False
        if os.path.exists(f_path):
            try:
                with open(f_path, 'rb') as f:
                    data = pickle.load(f)
                    self.dt_gf = pickle.load(f)
                    self.dt_stf = pickle.load(f)
            except:
                data = self.__request_db(model, station, origin, data_type)
                b_save = True
        else:
            data = self.__request_db(model, station, origin, data_type)
            b_save = True

        # Save it as pickle file for future use.
        if b_save:
            try:
                with open(f_path, 'wb') as f:
                    pickle.dump(data, f)
                    pickle.dump(self.dt_gf, f)
                    pickle.dump(self.dt_stf, f)
            except:
                pass

        return data


    def request_sgt(self, model, station, origin, save_dir, data_type='SGT'):
        '''Request SGT.'''
        return self.__read_or_download(model, station, origin, save_dir, data_type)

    def request_dgf(self, model, station, origin, save_dir, data_type='DGF'):
        '''Request DGF.'''
        return self.__read_or_download(model, station, origin, save_dir, data_type)

    def request_model_info(self, model):
        '''Requst model parameters.'''
        info_dt = self.__request_model_info(model)

        info_str = 'minimum latitude: %.4f \n' \
                   'maximum latitude: %.4f \n' \
                   'delta of latitude: %.4f \n' \
                   'minimum longitude: %.4f \n' \
                   'maximum longitude: %.4f \n' \
                   'delta of longitude: %.4f \n' \
                   'minimum depth (m): %.2f \n' \
                   'maximum depth (m): %.2f \n' \
                   'delta of depth (m): %.2f \n' % (info_dt.get('lat_min'),
                                                    info_dt.get('lat_max'),
                                                    info_dt.get('lat_delta'),
                                                    info_dt.get('long_min'),
                                                    info_dt.get('long_max'),
                                                    info_dt.get('long_delta'),
                                                    info_dt.get('depth_min'),
                                                    info_dt.get('depth_max'),
                                                    info_dt.get('depth_delta'))
        return info_dt, info_str


class SeisClient(SeisClientBase):
    '''
    Request Greens function and synthetic waveform from remote database.

    * SGT and DGF are from remote server,
    * Other Greens function and synthetic waveform by SeisGen.
    '''

    def __init__(self, db_url=None, db_port=None):
        super().__init__(db_url=db_url, db_port=db_port)

    def get_greens_fk(self, model, station, origin, save_dir):
        '''
            Request FK-type Greens function.
            SGT from server, FKGF by SeisGen.
        '''

        sgt = self.request_sgt(model, station, origin, save_dir, data_type='SGT')
        fk = DSGTMgr(None, None, None, True).set_dt(self.dt_gf).get_fk_greens_function_next(sgt, station, origin)

        # from m/(n.m) -> the unit of fk-type Greens function :10^-20 cm/(dyne cm)
        factor = 1E15
        for tr in fk:
            tr.data = tr.data * factor
        return fk

    def get_greens_3DMT(self, model, station, origin, save_dir):
        '''
        Request 3D MT Greens function.
        SGT from server, 3D Greens by SeisGen.

        :param model:   The identifier (name) of 3D background model.
        :param station: An instance of the obspy AttribDict class. For example:
                        station = AttribDict({ 'latitude': 34.0210,
                                                'longitude': -118.287,
                                                'network': 'CI',
                                                'station': 'USC',
                                                'location': '',
                                                'id': 'USC'})

        :param origin:  An instance of the obspy AttribDict class. For example:
                        origin = Origin({'time': '2019-07-04T18:39:44.0000Z',
                                              'latitude': 35.601333,
                                              'longitude': -117.597,
                                              'depth_in_m': 2810.0,
                                              'id': 'evt11056825'})
        :param save_dir: The directory to store the downloaded data.
        '''
        sgt = self.request_sgt(model, station, origin, save_dir, data_type='SGT')
        grn3d = DSGTMgr(None, None, None, True).set_dt(self.dt_gf).get_greens_function_next(sgt, station, origin)
        return grn3d


    def get_synthetic_mtsolution(self, model, station, origin, save_dir, mt_RTP, b_RTZ=False):
        '''
        Request synthetic waveform by moment tensor solution.
        SGT from server, synthetic waveform by SeisGen.

        :param model:   The identifier (name) of 3D background model.
        :param station: An instance of the obspy AttribDict class. For example:
                        station = AttribDict({ 'latitude': 34.0210,
                                                'longitude': -118.287,
                                                'network': 'CI',
                                                'station': 'USC',
                                                'location': '',
                                                'id': 'USC'})

        :param origin:  An instance of the obspy AttribDict class. For example:
                        origin = Origin({'time': '2019-07-04T18:39:44.0000Z',
                                              'latitude': 35.601333,
                                              'longitude': -117.597,
                                              'depth_in_m': 2810.0,
                                              'id': 'evt11056825'})
        :param save_dir: The directory to store the downloaded data.
        :param mt_RTP:    CMTSOLUTION, moment tensor in RTP [Mrr, Mtt, Mpp, Mrt, Mrp, Mtp]
        :param b_RTZ:     Convert the synthetic waveform in RTZ if True, otherwise in ENZ.
        '''
        sgt = self.request_sgt(model, station, origin, save_dir, data_type='SGT')
        syn = DSGTMgr(None, None, None, True).set_dt(self.dt_gf).get_waveform_next(sgt, station, origin, mt_RTP, b_RTZ)
        return syn


    def get_greens_force(self, model, station, origin, save_dir):
        '''
        Get Greens function from unit-force origins.

        :param model:   The identifier (name) of 3D background model.
        :param station: An instance of the obspy AttribDict class. For example:
                        station = AttribDict({ 'latitude': 34.0210,
                                                'longitude': -118.287,
                                                'network': 'CI',
                                                'station': 'USC',
                                                'location': '',
                                                'id': 'USC'})

        :param origin:  An instance of the obspy AttribDict class. For example:
                        origin = Origin({'time': '2019-07-04T18:39:44.0000Z',
                                              'latitude': 35.601333,
                                              'longitude': -117.597,
                                              'depth_in_m': 2810.0,
                                              'id': 'evt11056825'})
        :param save_dir: The directory to store the downloaded data.
        '''

        dgf = self.request_dgf(model, station, origin, save_dir, data_type='DGF')
        greens = DDGFMgr(None, None, None, True).set_dt(self.dt_gf).get_greens_function_next(dgf, station)
        return greens


    def get_synthetic_forcesolution(self, model, station, origin, save_dir, force_enz, b_RTZ=False):
        '''
        Get synthetic waveform from the force solution in ENZ convention.

        :param model:   The identifier (name) of 3D background model.
        :param station: An instance of the obspy AttribDict class. For example:
                        station = AttribDict({ 'latitude': 34.0210,
                                                'longitude': -118.287,
                                                'network': 'CI',
                                                'station': 'USC',
                                                'location': '',
                                                'id': 'USC'})

        :param origin:  An instance of the obspy AttribDict class. For example:
                        origin = Origin({'time': '2019-07-04T18:39:44.0000Z',
                                              'latitude': 35.601333,
                                              'longitude': -117.597,
                                              'depth_in_m': 2810.0,
                                              'id': 'evt11056825'})
        :param save_dir: The directory to store the downloaded data.
        :param force_enz: The FORCESOLUTION (E, N ,Z)
        :param b_RTZ:     Convert the synthetic waveform in RTZ if True, otherwise in ENZ.
        :return:
        '''

        dgf = self.request_dgf(model, station, origin, save_dir, data_type='DGF')
        syn = DDGFMgr(None, None, None, True).set_dt(self.dt_gf).get_waveform_next(dgf, station, origin, force_enz, b_RTZ)
        return syn
