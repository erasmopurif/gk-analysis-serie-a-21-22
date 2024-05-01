import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from mplsoccer.pitch import Pitch, VerticalPitch
from mplsoccer import PyPizza, FontManager
from io import BytesIO
from PIL import Image
import requests
from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

font_normal = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotomono/' 'RobotoMono[wght].ttf')
font_italic = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotomono/' 'RobotoMono-Italic[wght].ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/' 'RobotoSlab%5Bwght%5D.ttf')


# Page config
st.set_page_config(
    page_title="Goalkeeper Analysis",
    page_icon="⚽️",
    layout="wide"
)

# Load datasets
@st.cache_resource
def load_datasets():
    df_gk_info_ids = pd.read_csv("data/gk_info_ids.csv")
    df_gk_stats = pd.read_csv("data/gk_stats_filter.csv")
    df_goal_kick = pd.read_csv("data/soccerment_serieA_2021-22_goal_kick.csv")
    df_goals = pd.read_csv("data/soccerment_serieA_2021-22_goals.csv", encoding='latin-1')
    df_goals["x"] = df_goals["x"].apply(lambda x: x if x > 70 else 100-x)
    df_gk_events = pd.read_csv("data/gk_events.csv")
    return df_gk_info_ids, df_gk_stats, df_goal_kick, df_goals, df_gk_events

df_gk_info_ids, df_gk_stats, df_goal_kick, df_goals, df_gk_events = load_datasets()


st.title("Goalkeeper Analyser - Serie A 2021/22")
st.markdown("#### by **:green[Erasmo Purificato]** ([Personal website](https://erasmopurif.com/))")
st.markdown("#")


def app_description():
    readme_md_file = Path("README.md").read_text()
    st.markdown(readme_md_file, unsafe_allow_html=True)


def single_gk_analysis():
    gk_name_list = sorted(df_gk_stats["full_name"].tolist())
    gk = st.selectbox(
        label="Select the goalkeeper to analyse",
        options=gk_name_list,
    )
    gk_opta_id = df_gk_stats.loc[df_gk_stats["full_name"] == gk, "opta_id"].item()
    color_info = "orange"
    color_basic_stats = "green"
    color_pizza_stats = "blue"

    gk_img, gk_info, gk_basic_stats, _ = st.columns([1,3,3,1])
    with gk_img:
        url = df_gk_info_ids.loc[df_gk_info_ids["opta_id"] == gk_opta_id, "Img"].item()
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        st.image(img) 
    with gk_info:
        st.markdown("##### **:"+color_info+"[Full name]**: " + gk)
        team = df_gk_info_ids.loc[df_gk_info_ids["opta_id"] == gk_opta_id, "Team"].item()
        st.markdown("##### **:"+color_info+"[Team]**: " + team)
        nationality = df_gk_info_ids.loc[df_gk_info_ids["opta_id"] == gk_opta_id, "Nationality"].item()
        st.markdown("##### **:"+color_info+"[Nationality]**: " + nationality)
        birth_date = df_gk_info_ids.loc[df_gk_info_ids["opta_id"] == gk_opta_id, "Birth date"].item()
        st.markdown("##### **:"+color_info+"[Birth date]**: " + birth_date)
        height = df_gk_info_ids.loc[df_gk_info_ids["opta_id"] == gk_opta_id, "Height"].item()
        st.markdown("##### **:"+color_info+"[Height]**: " + height)
    with gk_basic_stats:
        # st.markdown("#### **Basic stats**")
        appearances = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "appearances"].item()
        st.markdown("##### **:"+color_basic_stats+"[Appearances]**: " + str(appearances))
        minutes_played = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "mins_played"].item()
        st.markdown("##### **:"+color_basic_stats+"[Minutes played]**: " + str(minutes_played) + "'")
        goals_con = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Gol subiti"].item()
        st.markdown("##### **:"+color_basic_stats+"[Goals conceded]**: " + str(goals_con))
        saves = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Parate"].item()
        st.markdown("##### **:"+color_basic_stats+"[Total saves]**: " + str(saves))

    st.markdown("---")
    # st.markdown("## Metrics score comparison")

    gk_pizza, _, gk_pizza_stats = st.columns([3, 1, 3])
    with gk_pizza:
        st.markdown("#### Percentile Rank vs all Serie A Goalkeepers")
        gk_metrics_rank = [col for col in df_gk_stats.columns.tolist() if "RANK" in col]
        pizza_chart_params = [
            "% Saves per shot on target taken",
            "Minutes played per goal conceded",
            "Saves P90",
            "Passes (no goal kicks) P90",
            "Penalties saved P90",
            "Exits P90",
            "xG Blocked P90"
        ]
        values = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, gk_metrics_rank].values
        values_int = []
        for i in values[0]:
            values_int.append(int(i))

        baker = PyPizza(
            params=pizza_chart_params,      # list of parameters
            straight_line_color="#FFFFFF",  # color for straight lines
            straight_line_lw=1,             # linewidth for straight lines
            last_circle_color="#FFFFFF",    # color for the last circle
            last_circle_lw=1,               # linewidth of last circle
            other_circle_lw=1,              # linewidth for other circles
            other_circle_ls="-.",           # linestyle for other circles
            background_color="#0E1117"
        )
        # plot pizza
        fig, ax = baker.make_pizza(
            values_int,             # list of values
            figsize=(7,7),         # adjust figsize according to your need
            param_location=105,     # where the parameters will be added
            color_blank_space=None,
            kwargs_slices=dict(
                facecolor="royalblue", edgecolor="#FFFFFF",
                zorder=2, linewidth=2.5
            ),                   # values to be used when plotting slices
            kwargs_params=dict(
                color="#FFFFFF", fontsize=11,
                fontproperties=font_bold.prop, va="center"
            ),                   # values to be used when adding parameter
            kwargs_values=dict(
                color="#FFFFFF", fontsize=12,
                fontproperties=font_bold.prop, zorder=3,
                bbox=dict(
                    edgecolor="#FFFFFF", facecolor="royalblue",
                    boxstyle="round,pad=0.2", lw=2
                )
            )                   # values to be used when adding parameter-values
        )
        # add subtitle
        # fig.text(
        #     0.51, 0.95,
        #     "Percentile Rank vs all Serie A goalkeepers", size=15,
        #     ha="center", fontproperties=font_bold.prop, color="#FFFFFF")
        
        st.pyplot(fig)

    with gk_pizza_stats:
        st.markdown("#### Selected Goalkeeper's metrics scores")
        # Add vertical space
        st.markdown("#")
        st.markdown("#")
        # st.markdown("#")
        # st.markdown("#")

        # Display stats
        saves_per_shot = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "% parate su tiri in porta subiti"].item()
        saves_per_shot = round(saves_per_shot, 2)
        st.markdown("##### **:"+color_pizza_stats+"[% Saves per shot on target taken]**: " + str(saves_per_shot))
        mins_per_goal = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Minuti giocati / gol subiti"].item()
        mins_per_goal = round(mins_per_goal, 2)
        st.markdown("##### **:"+color_pizza_stats+"[Minutes played per goal conceded]**: " + str(mins_per_goal))
        saves_p90 = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Parate P90"].item()
        saves_p90 = round(saves_p90, 2)
        st.markdown("##### **:"+color_pizza_stats+"[Saves P90]**: " + str(saves_p90))
        passes_p90 = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Passaggi portiere P90"].item()
        passes_p90 = round(passes_p90, 2)
        st.markdown("##### **:"+color_pizza_stats+"[Passes (no goal kicks) P90]**: " + str(passes_p90))
        penalties_saved = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Rigori parati"].item()
        st.markdown("##### **:"+color_pizza_stats+"[Penalties saved]**: " + str(penalties_saved))
        penalties_p90 = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Rigori parati P90"].item()
        penalties_p90 = round(penalties_p90, 2)
        st.markdown("##### **:"+color_pizza_stats+"[Penalties saved P90]**: " + str(penalties_p90))
        exits_p90 = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "Uscite P90"].item()
        exits_p90 = round(exits_p90, 2)
        st.markdown("##### **:"+color_pizza_stats+"[Exits P90]**: " + str(exits_p90))
        xg_blocked_p90 = df_gk_stats.loc[df_gk_stats["opta_id"] == gk_opta_id, "xg_blocked_p90"].item()
        xg_blocked_p90 = round(xg_blocked_p90, 2)
        st.markdown("##### **:"+color_pizza_stats+"[xG Blocked P90]**: " + str(xg_blocked_p90))

    st.markdown("---")


    gk_goals_map, _, gk_goalkick_map = st.columns([4,1,4])
    with gk_goals_map:
        st.markdown("#### Goals Conceded Map")
        st.markdown("The heatmap displays the distribution of the goals conceded by the goalkeeper during the season, considering the point where the scorers made the shots.")

        df_gk_goals = df_goals[df_goals["opp_gk_id"] == gk_opta_id]

        pitch = VerticalPitch(pitch_type="opta", line_zorder=2, half=True, pitch_color="#0E1117", line_color="#FFFFFF")
        fig, ax = pitch.draw(figsize=(7,7))
        fig.set_facecolor("#0E1117")
        
        bin_statistic = pitch.bin_statistic(df_gk_goals.x, df_gk_goals.y, statistic="count", bins=(80,80))
        bin_statistic["statistic"] = gaussian_filter(bin_statistic["statistic"], 2)
        min_value = min(bin_statistic["statistic"].reshape(1,-1).flatten().tolist())
        max_value = max(bin_statistic["statistic"].reshape(1,-1).flatten().tolist())
        median_value = (min_value + max_value) / 2
        heatmap = pitch.heatmap(bin_statistic, cmap="mako", ax=ax) # YlGnBu

        # colors = matplotlib.colormaps["viridis"].resampled(256)
        # colors = matplotlib.colormaps["mako"].resampled(256)
        # new_colors = colors(np.linspace(0, 1, 256))
        # dark = np.array([14/256, 17/256, 23/256, 1])
        # new_colors[:5, :] = dark
        # custom_colormap = ListedColormap(new_colors)
        # heatmap = pitch.heatmap(bin_statistic, cmap=custom_colormap, ax=ax)

        pitch.scatter(
            x = df_gk_goals.x,
            y = df_gk_goals.y,
            s = 10,
            color = "black",
            zorder = 10,
            alpha = 0.1,
            ax = ax
        )
        cbar = plt.colorbar(heatmap, shrink=0.5, pad=0.01, ticks=[min_value, median_value, max_value])
        cbar.outline.set_edgecolor("#FFFFFF")
        cbar.ax.set_yticklabels(["Low", "Medium", "High"])
        cbar.ax.yaxis.set_tick_params(color="#FFFFFF")
        ticks = plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#FFFFFF")
        st.pyplot(fig)

    with gk_goalkick_map:
        st.markdown("#### Goal Kicks Map")
        st.markdown("The heatmap displays the distribution of the goal kicks carried out by the goalkeeper during the season, considering the end-point of the pass.")

        df_gk_goalkick = df_goal_kick[df_goal_kick["player_id"] == gk_opta_id]

        pitch = Pitch(pitch_type="opta", line_zorder=2, half=False, pitch_color="#0E1117", line_color="#FFFFFF")
        fig, ax = pitch.draw(figsize=(7,7))
        fig.set_facecolor("#0E1117")

        bin_statistic = pitch.bin_statistic(df_gk_goalkick.end_x, df_gk_goalkick.end_y, statistic="count", bins=(80,80))
        bin_statistic["statistic"] = gaussian_filter(bin_statistic["statistic"], 2)
        min_value = min(bin_statistic["statistic"].reshape(1,-1).flatten().tolist())
        max_value = max(bin_statistic["statistic"].reshape(1,-1).flatten().tolist())
        median_value = (min_value + max_value) / 2
        heatmap = pitch.heatmap(bin_statistic, cmap="mako", ax=ax, zorder=1)

        pitch.scatter(
            x = df_gk_goalkick.end_x,
            y = df_gk_goalkick.end_y,
            s = 10,
            color = "black",
            zorder = 3,
            alpha = 0.1,
            ax = ax
        )

        cbar = plt.colorbar(heatmap, shrink=0.5, pad=0.01, ticks=[min_value, median_value, max_value], location="bottom")
        cbar.outline.set_edgecolor("#FFFFFF")
        cbar.ax.set_xticklabels(["Low", "Medium", "High"])
        cbar.ax.xaxis.set_tick_params(color="#FFFFFF")
        ticks = plt.setp(plt.getp(cbar.ax.axes, "xticklabels"), color="#FFFFFF")
        st.pyplot(fig)

    st.markdown("---")

    # GK passes and average position on specific match
    st.markdown("#### Passes Distribution (*no goal kicks*) per Match and Average Position in Pass Plays")
    st.markdown("For each selected matchday, on the left hand side, the chart displays the **distribution of passes** (*no goal kicks*) made by the goalkeeper. On the opposite side of the chart, the :blue[blue] line (and related point in the pitch) represents the **average position** of the goalkeeper in the pass plays during the selected match, while the :green[green] line represents the **average position** of the goalkeeper in the pass plays during the entire season.")

    df_gk_events_id = df_gk_events[df_gk_events["player_id"] == gk_opta_id]
    matches = []
    matches_temp = []
    for matchday in list(set(df_gk_events_id["matchday"].tolist())):
        home_team = df_gk_events_id.loc[df_gk_events_id["matchday"] == matchday, "home_team"]
        away_team = df_gk_events_id.loc[df_gk_events_id["matchday"] == matchday, "away_team"]
        matches_temp.append("Matchday " + str(matchday) + " | " + home_team + " vs. " + away_team)
    for i in range(0,len(matches_temp)):
        matches.append(matches_temp[i].values[0])

    matchday_text = st.selectbox(
        label="Select a matchday",
        options=matches
    )

    matchday = int(matchday_text.split("|")[0].split(" ")[1])
    
    df_passes_match = df_gk_events_id[(df_gk_events_id["matchday"] == matchday) & (df_gk_events_id["type_id"] == 1) & (df_gk_events_id["goal_kick"] == False)]
    df_passes_match_agg = df_passes_match.groupby("player_id").agg({"x": ["mean"], "y": ["mean", "count"]})
    df_passes_match_agg.columns = ["avg_x", "avg_y", "pass_count"]
    
    df_passes_tot = df_gk_events_id[(df_gk_events_id["type_id"] == 1) & (df_gk_events_id["goal_kick"] == False)]
    df_passes_tot_agg = df_passes_tot.groupby("player_id").agg({"x": ["mean"], "y": ["mean", "count"]})
    df_passes_tot_agg.columns = ["avg_x", "avg_y", "pass_count"]

    _, gk_passes, _, = st.columns([1,4,1])

    with gk_passes:
        pitch = Pitch(pitch_type="opta", line_zorder=1, half=False, pitch_color="#0E1117", line_color="#FFFFFF")
        fig, ax = pitch.draw(figsize=(7,7))
        fig.set_facecolor("#0E1117")

        pitch.lines(
            df_passes_match.x,
            df_passes_match.y,
            df_passes_match.end_x,
            df_passes_match.end_y,
            lw=2,
            comet = True,
            #color = 'b',
            cmap = "mako",
            alpha = 1,
            ax=ax
        )
        pitch.scatter(
            x = df_passes_match.end_x,
            y = df_passes_match.end_y,
            s = 50,
            color = "#def5e5",
            # color = "yellow",
            edgecolor = "none",
            zorder = 5,
            ax = ax
        )
        avg_x = df_passes_match_agg.avg_x
        avg_y = df_passes_match_agg.avg_y
        pitch.scatter(
            x = 100 - avg_x,
            y = 100 - avg_y,
            s = 400,
            edgecolor = "azure",
            # color = "#72D4AD",
            color ="royalblue",
            zorder = 5,
            ax = ax
        )
        pitch.lines(100 - avg_x, 0, 100 - avg_x, 100, lw=1.5, color="royalblue", linestyle="dashed", zorder=3, ax=ax)
        avg_x_tot = df_passes_tot_agg.avg_x
        pitch.lines(100 - avg_x_tot, 0, 100 - avg_x_tot, 100, lw=1.5, color="green", linestyle="dotted", zorder=2, ax=ax)
        pitch.annotate(
            "GK",
            xy=(100-avg_x.item(),100-avg_y.item()),
            color="white",
            va="center",
            ha="center",
            size=9,
            # weight="bold",
            ax=ax,
            zorder=6
        )
        pitch.annotate(
            str(round(avg_x.item(),1)) + "m",
            xy=(100-avg_x.item(),15),
            bbox = dict(boxstyle="round,pad=0.3", edgecolor="azure", facecolor="royalblue"),
            color="white",
            va="center",
            ha="center",
            size=9,
            # weight="bold",
            ax=ax,
            zorder=5
        )
        pitch.annotate(
            str(round(avg_x_tot.item(),1)) + "m",
            xy=(100-avg_x_tot.item(),5),
            bbox = dict(boxstyle="round,pad=0.3", edgecolor="azure", facecolor="green"),
            color="white",
            va="center",
            ha="center",
            size=9,
            # weight="bold",
            ax=ax,
            zorder=5
        )

        st.pyplot(fig)


selected_page = option_menu(
    menu_title=None,
    options=["Description", "Goalkeeper analysis"],
    icons=["file-earmark-text", "person-check"],
    orientation="horizontal",
    menu_icon="cast",
    default_index=0
)
if selected_page == "Description":
    app_description()
elif selected_page == "Goalkeeper analysis":
    single_gk_analysis()