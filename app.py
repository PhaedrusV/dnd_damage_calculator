from flask import Flask, render_template, request
import plotly.graph_objects as go
import plotly
import json
import numpy as np
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Starting app.py")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
logger.debug("Flask app initialized")

def expected_die_value(num_dice, die_size):
    logger.debug(f"Calculating expected_die_value: num_dice={num_dice}, die_size={die_size}")
    return num_dice * (die_size + 1) / 2 if num_dice > 0 and die_size > 0 else 0

def calculate_damage(to_hit, x, y, v, w, z, sharpshooter=False, advantage=False, disadvantage=False):
    logger.debug(f"Calculating damage: to_hit={to_hit}, x={x}, y={y}, v={v}, w={w}, z={z}, sharpshooter={sharpshooter}, advantage={advantage}, disadvantage={disadvantage}")
    normal_dice = expected_die_value(x, y) + expected_die_value(v, w)
    crit_dice = 2 * (expected_die_value(x, y) + expected_die_value(v, w))
    static_bonus = z + (10 if sharpshooter else 0)
    effective_to_hit = to_hit + (5 if sharpshooter else 0)

    if advantage and not disadvantage:
        p_miss = max(0, (effective_to_hit - 1) / 20)
        p_hit = 1 - p_miss ** 2 if effective_to_hit <= 20 else 0
        p_crit = 1 - (19/20) ** 2
    elif disadvantage and not advantage:
        p_hit_single = max(0, (21 - effective_to_hit) / 20)
        p_hit = p_hit_single ** 2 if effective_to_hit <= 20 else 0
        p_crit = (1/20) ** 2
    else:
        p_hit = max(0, (21 - effective_to_hit) / 20) if effective_to_hit <= 20 else 0
        p_crit = 1/20

    if effective_to_hit >= 20:
        return p_crit * (crit_dice + static_bonus)
    
    p_normal_hit = max(0, p_hit - p_crit)
    return p_normal_hit * (normal_dice + static_bonus) + p_crit * (crit_dice + static_bonus)

def sanitize_input(value, min_val, max_val, default=0):
    logger.debug(f"Sanitizing input: value={value}, min_val={min_val}, max_val={max_val}, default={default}")
    try:
        val = int(value)
        return max(min_val, min(val, max_val))
    except (ValueError, TypeError):
        return default

@app.route('/', methods=['GET', 'POST'])
def index():
    logger.debug("Handling request to /")
    x, y, v, w, z = 1, 8, 0, 0, 4
    advantage, disadvantage = False, False

    if request.method == 'POST':
        x = sanitize_input(request.form.get('x', 0), 0, 100)
        y = sanitize_input(request.form.get('y', 0), 0, 100)
        v = sanitize_input(request.form.get('v', 0), 0, 100)
        w = sanitize_input(request.form.get('w', 0), 0, 100)
        z = sanitize_input(request.form.get('z', 0), -100, 100)
        advantage = 'advantage' in request.form
        disadvantage = 'disadvantage' in request.form

    logger.debug("Calculating damages")
    to_hit_range = np.arange(2, 21, 2)
    base_damages = [calculate_damage(t, x, y, v, w, z, False, advantage, disadvantage) for t in to_hit_range]
    sharp_damages = [calculate_damage(t, x, y, v, w, z, True, advantage, disadvantage) for t in to_hit_range]

    logger.debug("Creating Plotly figure")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=to_hit_range, y=base_damages, mode='lines', name='Base Damage', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=to_hit_range, y=sharp_damages, mode='lines', name='Sharpshooter', 
                            line=dict(color='red', dash='dash')))
    fig.update_layout(
        title='Expected Damage vs To-Hit Threshold',
        xaxis_title='To-Hit Threshold',
        yaxis_title='Expected Damage',
        xaxis=dict(tickmode='array', tickvals=to_hit_range),
        legend=dict(x=0.01, y=0.99),
        template='plotly_white'
    )

    logger.debug("Converting figure to JSON")
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    logger.debug("Rendering template")
    return render_template('index.html', graph_json=graph_json, x=x, y=y, v=v, w=w, z=z, 
                          advantage=advantage, disadvantage=disadvantage)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
