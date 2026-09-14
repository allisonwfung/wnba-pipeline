import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle
import numpy as np

# load data — cached so it doesn't reload every time
@st.cache_data
def load_data():
    df = pd.read_csv('wnba_data.csv')
    return df

# paste your draw_court function here
# cite : http://savvastjortjoglou.com/nba-shot-sharts.html

from matplotlib.patches import Circle, Rectangle, Arc

def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax
# paste your plot_shot_chart function here
def plot_shot_chart(pbp, player_name, made_only=True):
    shots = pbp[
        (pbp['shooting_play'] == True) & 
        (~pbp['type_text'].str.contains('Free Throw', na=False)) &
        (pbp['athlete_name_1'] == player_name)
    ].copy()
    
    if made_only:
        shots = shots[shots['scoring_play'] == True]
    
    shots['x'] = (shots['coordinate_x'] - 25) * 10
    shots['y'] = shots['coordinate_y'] * 10
    shots = shots[shots['y'] <= 300]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#f8f8f8')
    ax.set_aspect('equal')
    ax.set_facecolor('#f8f8f8')
    
    ax.hexbin(shots['x'], shots['y'],
              gridsize=15, cmap='Blues',
              alpha=1.0, mincnt=1)
        
    # court drawn ON TOP of hexagons
    draw_court(ax, color='black', outer_lines=True)
    
    ax.set_xlim(-250, 250)
    ax.set_ylim(-47.5, 280)
    ax.set_axis_off()
    
    shot_type = "Made Field Goals" if made_only else "Field Goal Attempts"
    ax.set_title(f'{player_name}\n{shot_type} — 2026 WNBA Season',
                 fontsize=16, pad=20)
    
    ax.text(-240, 260, 'Data: ESPN API | github.com/allisonwfung', color='grey', fontsize=9)
    
    return fig

# app layout
# player selector at top
st.set_page_config(page_title='WNBA Shot Charts', layout='wide')
st.title('🏀 WNBA Shot Charts 2026')
st.caption('Data: ESPN API | Updated daily')

pbp = load_data()

player_list = sorted(pbp['athlete_name_1'].dropna().unique())
player = st.selectbox('Select a player', player_list)
made_only = st.toggle('Made shots only', value=True)

if st.button('Generate Chart'):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = plot_shot_chart(pbp, player, made_only)
        st.pyplot(fig)
    
    with col2:
        st.subheader(f"{player}")
        st.info("📊 Stats coming soon")