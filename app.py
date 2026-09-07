import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --------------------------------------------------------------------------
# Load the trained model and the dataframe used for generating dropdown options.
# ---------------------------------------------------------------------------
pipe = pickle.load(open('pipe.pkl', 'rb'))
df = pickle.load(open('df.pkl', 'rb'))

# Fixed dropdown options carried over exactly from the Streamlit version.
RAM_OPTIONS = [2, 4, 6, 8, 12, 16, 24, 32, 64]
HDD_OPTIONS = [0, 128, 256, 512, 1024, 2048]
SSD_OPTIONS = [0, 8, 128, 256, 512, 1024]
RESOLUTION_OPTIONS = [
    '1920x1080', '1366x768', '1600x900', '3840x2160', '3200x1800',
    '2880x1800', '2560x1600', '2560x1440', '2304x1440'
]


def get_form_options():
    """Options pulled from the dataframe, same source as st.selectbox(df[...].unique())."""
    return {
        'companies': sorted(df['Company'].unique().tolist()),
        'types': sorted(df['TypeName'].unique().tolist()),
        'cpus': sorted(df['Cpu brand'].unique().tolist()),
        'gpus': sorted(df['Gpu brand'].unique().tolist()),
        'os_list': sorted(df['os'].unique().tolist()),
        'ram_options': RAM_OPTIONS,
        'hdd_options': HDD_OPTIONS,
        'ssd_options': SSD_OPTIONS,
        'resolution_options': RESOLUTION_OPTIONS,
    }


@app.route('/')
def home():
    return render_template('index.html', **get_form_options())


@app.route('/predict', methods=['POST'])
def predict():
    """Mirrors the query-building logic from the original Streamlit app.py exactly."""
    try:
        data = request.get_json(force=True)

        company = data['company']
        type_name = data['type']
        ram = int(data['ram'])
        weight = float(data['weight'])
        touchscreen = 1 if data['touchscreen'] == 'Yes' else 0
        ips = 1 if data['ips'] == 'Yes' else 0
        screen_size = float(data['screen_size'])
        resolution = data['resolution']
        cpu = data['cpu']
        hdd = int(data['hdd'])
        ssd = int(data['ssd'])
        gpu = data['gpu']
        os_name = data['os']

        x_res, y_res = (int(v) for v in resolution.split('x'))
        ppi = ((x_res ** 2) + (y_res ** 2)) ** 0.5 / screen_size

        query = pd.DataFrame({
            'Company': [company],
            'TypeName': [type_name],
            'Ram': [ram],
            'Weight': [weight],
            'Touchscreen': [touchscreen],
            'Ips': [ips],
            'ppi': [ppi],
            'Cpu brand': [cpu],
            'HDD': [hdd],
            'SSD': [ssd],
            'Gpu brand': [gpu],
            'os': [os_name]
        })

        prediction = pipe.predict(query)[0]
        price = int(prediction)

        return jsonify({'success': True, 'price': price})

    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400


if __name__ == '__main__':
    app.run(debug=True)
