# -------------------------------------------------------------------
# Request synthetic waveform from finite fault.
#
# Author: Liang Ding
# Email: myliang.ding@mail.utoronto.ca
# -------------------------------------------------------------------

from seisclient.seisclient import SeisClient
from obspy.core.util.attribdict import AttribDict
from obspy.core.stream import Stream

import numpy as np
import pandas as pd

def request_syn():

    req = SeisClient()

    # set model
    model = 'SOCAL3D'

    # station (CI.SLA)
    station = AttribDict({
        'latitude': 35.890,
        'longitude': -117.283,
        'network': 'CI',
        'station': 'SLA',
        'location': '',
        'id': 'SLA'})

    # set the directory to store the request data.
    save_dir = '/home/dingl/temp'

    # load finite fault model
    ff_df = pd.read_csv('finite_fault.csv')
    n_patches = len(ff_df)

    st = Stream()
    for i in range(n_patches):
        # source
        origin = AttribDict({'latitude': ff_df.loc[i]['latitude'],
                             'longitude': ff_df.loc[i]['longitude'],
                             'depth_in_m': ff_df.loc[i]['depth_in_m'],
                             'id': 'patch%s' % (ff_df.loc[i]['pid'])})

        mt_cmt = np.array([ff_df.loc[i]['mrr'], ff_df.loc[i]['mtt'], ff_df.loc[i]['mpp'],
                           ff_df.loc[i]['mrt'], ff_df.loc[i]['mrp'], ff_df.loc[i]['mtp']]) / 1E7

        syn = req.get_synthetic_mtsolution(model=model, station=station, origin=origin, save_dir=save_dir,
                                           mt_RTP=mt_cmt, b_RTZ=True)

        if i == 0:
            st = syn.copy()
            for tr in st:
                tr.data *= 1.0/n_patches
        else:
            for tr in st:
                tr.data += 1.0/n_patches * syn.select(channel=tr.stats.channel).traces[0].data

    print(st)
    st.plot()


if __name__ == '__main__':
    request_syn()