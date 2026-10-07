import streamlit as st
import os
import time
import pandas as pd
import base64

from dotenv import load_dotenv

load_dotenv(override=True)


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


# =========================================================
# AUTH
# =========================================================

from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults


# =========================================================
# CONFIG
# =========================================================

from services.config.workout_config import EXERCISE_OPTIONS


# =========================================================
# UI
# =========================================================

from services.ui.style_loader import (
    load_css,
    inject_local_font,
    inject_webrtc_styles
)


# =========================================================
# DATABASE
# =========================================================

from services.persistence.exercise_repository import (
    init_db,
    get_users_exercises,
    add_exercise
)


# =========================================================
# WEBRTC
# =========================================================

from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode
)


# =========================================================
# VISION
# =========================================================

from services.vision.exercise_video_processor import (
    VideoProcessorClass
)


# =========================================================
# METRICS
# =========================================================

from services.tracking.metrics import (
    sync_metrics_update
)


# =========================================================
# GROQ
# =========================================================

from groq import Groq


# =========================================================
# COACHING
# =========================================================

from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech

from services.coaching.voice_pipeline import (
    VoicePipeline,
    autoplay_audio
)


# =========================================================
# BACKGROUND
# =========================================================

def set_background():

    image_path = os.path.join(
        STATIC_DIR,
        "background.jpg"
    )

    if not os.path.exists(image_path):
        return

    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image:
                    linear-gradient(
                        rgba(0, 0, 0, 0.15),
                        rgba(0, 0, 0, 0.15)
                    ),
                    url("data:image/jpeg;base64,{encoded_image}");

                background-size: cover !important;
                background-position: center center !important;
                background-repeat: no-repeat !important;
                background-attachment: fixed !important;
            }}

            [data-testid="stAppViewContainer"] {{
                background: transparent !important;
            }}

            [data-testid="stAppViewContainer"] > .main {{
                background: transparent !important;
            }}

            [data-testid="stHeader"] {{
                background: transparent !important;
            }}

            [data-testid="stToolbar"] {{
                background: transparent !important;
            }}

            [data-testid="stSidebar"] {{
                background: rgba(8, 12, 18, 0.96) !important;
            }}

            /* Login title */
            .login-section h1,
            .login-section p {{
                color: #000000 !important;
            }}

            /* Summary */
            .summary-exercise {{
                color: #000000 !important;
                font-size: 1.2rem;
                font-weight: 600;
                margin-top: 10px;
                margin-bottom: 20px;
            }}

            /* History table */
            [data-testid="stTable"] {{
                color: #000000 !important;
            }}

            [data-testid="stTable"] table {{
                color: #000000 !important;
                background-color: #ffffff !important;
            }}

            [data-testid="stTable"] th,
            [data-testid="stTable"] td {{
                color: #000000 !important;
                background-color: #ffffff !important;
            }}

            </style>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:
        print("Background error:", e)


# =========================================================
# SESSION DEFAULTS
# =========================================================

def ensure_session_defaults():

    defaults = {
        "audio_to_play": None,
        "coach_feedback": None,
        "sets_completed": 0,
        "current_set_reps": 0,
        "workout_completed": False,
        "last_voice_rep": 0,
        "last_saved_sets_completed": 0,
        "last_notified_sets_completed": 0,
        "last_notified_workout_complete": False,
        "final_workout_summary": None,
        "current_page": "workout",
        "final_voice_played": False,
        "workout_started": False,

        # Safe workout-plan defaults
        "plan_sets": 3,
        "plan_reps": 10,

        "target_sets": 3,
        "reps_per_set": 10,
        "reps": 0,
        "current_set_reps": 0,

        "exercise_type": EXERCISE_OPTIONS[0]
        if EXERCISE_OPTIONS
        else "Squats",
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value

        # Safety for old session values
        if key in ["plan_sets", "plan_reps", "target_sets", "reps_per_set"]:

            try:
                if int(st.session_state[key]) < 1:
                    st.session_state[key] = 1
            except Exception:
                st.session_state[key] = 1


# =========================================================
# WORKOUT SUMMARY PAGE
# =========================================================

def render_workout_summary_page():

    st.title("🏋️ AI Real-time GYM Coach")

    st.subheader("Workout Summary")

    st.divider()

    summary = st.session_state.get(
        "final_workout_summary",
        {}
    )

    if not summary:

        st.info("No completed workout found.")

        if st.button(
            "🏋️ Start New Workout",
            width="stretch"
        ):

            reset_workout_state()

            st.rerun()

        return

    exercise = summary.get(
        "exercise",
        "Unknown"
    )

    sets_completed = summary.get(
        "sets_completed",
        0
    )

    target_sets = summary.get(
        "target_sets",
        0
    )

    total_reps = summary.get(
        "total_reps",
        0
    )

    target_reps = summary.get(
        "target_reps",
        0
    )

    performance = summary.get(
        "performance",
        "incomplete"
    )

    # -----------------------------------------------------
    # FINAL AUDIO
    # -----------------------------------------------------

    if (
        st.session_state.get("audio_to_play")
        and not st.session_state.get(
            "final_voice_played",
            False
        )
    ):

        try:

            autoplay_audio(
                st.session_state.audio_to_play
            )

            st.session_state.final_voice_played = True

        except Exception as e:

            print(
                "Final audio error:",
                e
            )

    # -----------------------------------------------------
    # EXERCISE
    # -----------------------------------------------------

    st.markdown(
        f"### 🏋️ Exercise: {exercise}"
    )

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🎯 Sets Completed",
            f"{sets_completed} / {target_sets}"
        )

    with col2:

        st.metric(
            "🔁 Total Reps",
            f"{total_reps} / {target_reps}"
        )

    with col3:

        st.metric(
            "💪 Performance",
            performance.capitalize()
        )

    st.divider()

    # -----------------------------------------------------
    # WORKOUT HISTORY
    # -----------------------------------------------------

    st.subheader("📊 Workout History")

    user_id = st.session_state.get(
        "user_id"
    )

    if isinstance(user_id, int):

        try:

            history_rows = get_users_exercises(
                user_id
            )

            rows = []

            for row in history_rows:

                rows.append(
                    {
                        "Exercise": row["exercise_name"],
                        "Date": row["created_at"],
                        "Reps": row["reps"],
                        "Sets": row["sets"],
                        "Time (sec)": row["time"],
                    }
                )

            df = pd.DataFrame(rows)

            if not df.empty:

                try:

                    df["Date"] = pd.to_datetime(
                        df["Date"]
                    )

                    df = df.sort_values(
                        by="Date",
                        ascending=False
                    )

                    df["Date"] = df["Date"].dt.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                except Exception:
                    pass

                df.insert(
                    0,
                    "#",
                    range(
                        1,
                        len(df) + 1
                    )
                )

                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True
                )

            else:

                st.info(
                    "Aaj se koi workout history nahi hai."
                )

        except Exception as e:

            print(
                "History error:",
                e
            )

            st.info(
                "Workout history load nahi ho payi."
            )

    else:

        st.info(
            "No workout history found."
        )

    st.divider()

    # -----------------------------------------------------
    # NEW WORKOUT
    # -----------------------------------------------------

    if st.button(
        "🏋️ Start New Workout",
        width="stretch",
        key="start_new_workout_button"
    ):

        reset_workout_state()

        st.rerun()


# =========================================================
# RESET WORKOUT
# =========================================================

def reset_workout_state():

    st.session_state.workout_started = False
    st.session_state.workout_completed = False

    st.session_state.current_page = "workout"

    st.session_state.final_workout_summary = None

    st.session_state.audio_to_play = None
    st.session_state.coach_feedback = None

    st.session_state.final_voice_played = False

    st.session_state.sets_completed = 0
    st.session_state.current_set_reps = 0
    st.session_state.reps = 0

    st.session_state.last_voice_rep = 0
    st.session_state.last_saved_sets_completed = 0
    st.session_state.last_notified_sets_completed = 0
    st.session_state.last_notified_workout_complete = False


# =========================================================
# VOICE PIPELINE
# =========================================================

def initialize_voice_pipeline():

    if "voice_pipeline" in st.session_state:

        return

    try:

        api_key = os.environ.get(
            "GROQ_API_KEY",
            ""
        )

        if (
            not api_key
            and hasattr(st, "secrets")
            and "GROQ_API_KEY" in st.secrets
        ):

            api_key = st.secrets[
                "GROQ_API_KEY"
            ]

        if not api_key:

            print(
                "GROQ API KEY NOT FOUND"
            )

            st.session_state.voice_pipeline = None

            return

        groq_client = Groq(
            api_key=api_key
        )

        llm_coach = LLMCoach(
            groq_client
        )

        tts = TextToSpeech()

        st.session_state.voice_pipeline = VoicePipeline(
            llm_coach,
            tts
        )

        print(
            "VOICE PIPELINE CREATED"
        )

    except Exception as e:

        print(
            "VOICE PIPELINE ERROR:",
            e
        )

        st.session_state.voice_pipeline = None


# =========================================================
# START WORKOUT
# =========================================================

def start_workout(
    exercise,
    target_sets,
    target_reps
):

    st.session_state.exercise_type = exercise

    st.session_state.target_sets = max(
        1,
        int(target_sets)
    )

    st.session_state.reps_per_set = max(
        1,
        int(target_reps)
    )

    st.session_state.reps = 0
    st.session_state.sets_completed = 0
    st.session_state.current_set_reps = 0

    st.session_state.last_voice_rep = 0
    st.session_state.last_saved_sets_completed = 0
    st.session_state.last_notified_sets_completed = 0
    st.session_state.last_notified_workout_complete = False

    st.session_state.workout_started = True
    st.session_state.workout_completed = False

    st.session_state.current_page = "workout"

    st.session_state.final_voice_played = False

    st.session_state.workout_started_at = time.time()

    st.session_state.set_cycle_started_at = time.time()

    st.session_state.final_workout_summary = None

    st.session_state.coach_feedback = None
    st.session_state.audio_to_play = None

    # -----------------------------------------------------
    # START VOICE
    # -----------------------------------------------------

    pipeline = st.session_state.get(
        "voice_pipeline"
    )

    if pipeline:

        try:

            result = pipeline.process_event(
                event="workout_started",
                exercise=exercise,
                metrics={}
            )

            if result:

                (
                    st.session_state.audio_to_play,
                    st.session_state.coach_feedback
                ) = result

        except Exception as e:

            print(
                "Start voice error:",
                e
            )


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    workout_started = st.session_state.get(
        "workout_started",
        False
    )

    with st.sidebar:

        # IMPORTANT:
        # No custom HTML here.
        # This prevents raw HTML appearing on screen.

        st.title(
            "🏋️‍♂️ Apna AI Coach"
        )

        username = st.session_state.get(
            "username"
        )

        if username:

            st.caption(
                f"👤 Logged in as {username}"
            )

        st.divider()

        # =================================================
        # BEFORE WORKOUT
        # =================================================

        if not workout_started:

            st.subheader(
                "Workout Plan"
            )

            plan_exercise = st.selectbox(
                "Exercise",
                options=EXERCISE_OPTIONS,
                key="plan_exercise"
            )

            # Safe sets
            current_sets = st.session_state.get(
                "plan_sets",
                3
            )

            try:
                current_sets = max(
                    1,
                    int(current_sets)
                )
            except Exception:
                current_sets = 3

            plan_sets = st.number_input(
                "Target Sets",
                min_value=1,
                max_value=20,
                value=current_sets,
                step=1,
                key="plan_sets"
            )

            # Safe reps
            current_reps = st.session_state.get(
                "plan_reps",
                10
            )

            try:
                current_reps = max(
                    1,
                    int(current_reps)
                )
            except Exception:
                current_reps = 10

            plan_reps = st.number_input(
                "Reps Per Set",
                min_value=1,
                max_value=100,
                value=current_reps,
                step=1,
                key="plan_reps"
            )

            st.write("")

            if st.button(
                "▶️ Start Workout",
                width="stretch",
                key="start_session_button"
            ):

                start_workout(
                    plan_exercise,
                    plan_sets,
                    plan_reps
                )

                st.rerun()

        # =================================================
        # DURING WORKOUT
        # =================================================

        else:

            exercise = st.session_state.get(
                "exercise_type",
                "Squats"
            )

            target_sets = max(
                1,
                int(
                    st.session_state.get(
                        "target_sets",
                        1
                    )
                )
            )

            target_reps = max(
                1,
                int(
                    st.session_state.get(
                        "reps_per_set",
                        10
                    )
                )
            )

            completed_reps = st.session_state.get(
                "reps",
                0
            )

            completed_sets = st.session_state.get(
                "sets_completed",
                0
            )

            current_set_reps = st.session_state.get(
                "current_set_reps",
                0
            )

            # -------------------------------------------------
            # PLAN
            # -------------------------------------------------

            st.subheader(
                "Workout Plan"
            )

            st.info(
                f"🏋️ {exercise}"
            )

            st.markdown(
                f"🎯 **{target_sets} Sets × {target_reps} Reps**"
            )

            st.divider()

            # -------------------------------------------------
            # LIVE WORKOUT
            # -------------------------------------------------

            st.subheader(
                "📊 Live Workout"
            )

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Reps",
                    completed_reps
                )

            with c2:

                st.metric(
                    "Sets",
                    f"{completed_sets} / {target_sets}"
                )

            st.metric(
                "Current Set Reps",
                f"{current_set_reps} / {target_reps}"
            )

            st.divider()

            # -------------------------------------------------
            # EXERCISE METRICS
            # -------------------------------------------------

            st.subheader(
                f"🏋️ {exercise} Metrics"
            )

            if exercise == "Squats":

                knee_angle = st.session_state.get(
                    "knee_angle",
                    0
                )

                back_angle = st.session_state.get(
                    "back_angle",
                    0
                )

                depth_status = st.session_state.get(
                    "depth_status",
                    "N/A"
                )

                st.metric(
                    "Knee Angle",
                    f"{knee_angle}°"
                )

                st.metric(
                    "Back Angle",
                    f"{back_angle}°"
                )

                st.metric(
                    "Depth Status",
                    depth_status
                )

            elif exercise == "Push-ups":

                elbow_angle = st.session_state.get(
                    "elbow_angle",
                    0
                )

                body_alignment = st.session_state.get(
                    "body_alignment",
                    "N/A"
                )

                hip_status = st.session_state.get(
                    "hip_status",
                    "N/A"
                )

                st.metric(
                    "Elbow Angle",
                    f"{elbow_angle}°"
                )

                st.metric(
                    "Body Alignment",
                    body_alignment
                )

                st.metric(
                    "Hip Position",
                    hip_status
                )

            elif exercise == "Biceps Curls (Dumbbell)":

                elbow_angle = st.session_state.get(
                    "elbow_angle",
                    0
                )

                shoulder_status = st.session_state.get(
                    "shoulder_status",
                    "N/A"
                )

                swing_status = st.session_state.get(
                    "swing_status",
                    "N/A"
                )

                st.metric(
                    "Elbow Angle",
                    f"{elbow_angle}°"
                )

                st.metric(
                    "Shoulder Stability",
                    shoulder_status
                )

                st.metric(
                    "Swing Detection",
                    swing_status
                )

            elif exercise == "Shoulder Press":

                elbow_angle = st.session_state.get(
                    "elbow_angle",
                    0
                )

                extension_status = st.session_state.get(
                    "extension_status",
                    "N/A"
                )

                back_arch_status = st.session_state.get(
                    "back_arch_status",
                    "N/A"
                )

                st.metric(
                    "Elbow Angle",
                    f"{elbow_angle}°"
                )

                st.metric(
                    "Arm Extension",
                    extension_status
                )

                st.metric(
                    "Back Arch",
                    back_arch_status
                )

            elif exercise == "Lunges":

                front_knee_angle = st.session_state.get(
                    "front_knee_angle",
                    0
                )

                torso_angle = st.session_state.get(
                    "torso_angle",
                    0
                )

                balance_status = st.session_state.get(
                    "balance_status",
                    "N/A"
                )

                st.metric(
                    "Front Knee Angle",
                    f"{front_knee_angle}°"
                )

                st.metric(
                    "Torso Angle",
                    f"{torso_angle}°"
                )

                st.metric(
                    "Balance Status",
                    balance_status
                )

            st.divider()

            # -------------------------------------------------
            # END WORKOUT
            # -------------------------------------------------

            if st.button(
                "🔴 End Workout",
                key="end_session_button",
                width="stretch"
            ):

                finish_workout()


# =========================================================
# FINISH WORKOUT
# =========================================================

def finish_workout():

    final_exercise = st.session_state.get(
        "exercise_type",
        "Unknown"
    )

    final_sets = st.session_state.get(
        "sets_completed",
        0
    )

    final_reps = st.session_state.get(
        "reps",
        0
    )

    target_sets = max(
        1,
        int(
            st.session_state.get(
                "target_sets",
                1
            )
        )
    )

    target_reps = max(
        1,
        int(
            st.session_state.get(
                "reps_per_set",
                10
            )
        )
    )

    target_total_reps = (
        target_sets * target_reps
    )

    # -----------------------------------------------------
    # TIME
    # -----------------------------------------------------

    workout_started_at = st.session_state.get(
        "workout_started_at"
    )

    if workout_started_at:

        workout_time = int(
            time.time()
            - workout_started_at
        )

    else:

        workout_time = 0

    # -----------------------------------------------------
    # PERFORMANCE
    # -----------------------------------------------------

    if (
        final_sets >= target_sets
        and final_reps >= target_total_reps
        and target_total_reps > 0
    ):

        performance = "excellent"

    elif (
        final_sets > 0
        or final_reps > 0
    ):

        performance = "good"

    else:

        performance = "incomplete"

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    user_id = st.session_state.get(
        "user_id"
    )

    if user_id is not None:

        try:

            add_exercise(
                user_id=user_id,
                exercise_name=final_exercise,
                reps=final_reps,
                sets=final_sets,
                time=workout_time
            )

            print(
                "WORKOUT SAVED"
            )

        except Exception as e:

            print(
                "DATABASE SAVE ERROR:",
                e
            )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    st.session_state.final_workout_summary = {

        "exercise": final_exercise,

        "sets_completed": final_sets,

        "target_sets": target_sets,

        "total_reps": final_reps,

        "target_reps": target_total_reps,

        "performance": performance
    }

    # -----------------------------------------------------
    # FINAL VOICE
    # -----------------------------------------------------

    st.session_state.final_voice_played = False

    pipeline = st.session_state.get(
        "voice_pipeline"
    )

    if pipeline:

        try:

            result = pipeline.process_event(

                event="workout_completed",

                exercise=final_exercise,

                metrics={
                    "sets_completed": final_sets,
                    "total_reps": final_reps,
                    "target_sets": target_sets,
                    "reps_per_set": target_reps,
                    "performance": performance
                }
            )

            if result:

                (
                    st.session_state.audio_to_play,
                    st.session_state.coach_feedback
                ) = result

        except Exception as e:

            print(
                "Final voice error:",
                e
            )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    st.session_state.workout_started = False

    st.session_state.workout_completed = True

    st.session_state.current_page = "summary"

    st.session_state.last_notified_workout_complete = True

    st.rerun()


# =========================================================
# MAIN PAGE
# =========================================================

def render_main_page():

    workout_started = st.session_state.get(
        "workout_started",
        False
    )

    # =====================================================
    # PAGE TITLE
    # =====================================================

    # IMPORTANT:
    # NO CUSTOM HTML HERE.
    # This prevents the <h1> / <p> code from appearing.

    st.title(
        "🏋️‍♂️ AI Real-time GYM Trainer"
    )

    st.markdown(
        "#### Real-time pose detection with proactive AI voice coaching"
    )

    # =====================================================
    # AUDIO
    # =====================================================

    if (
        workout_started
        and st.session_state.get(
            "audio_to_play"
        )
    ):

        try:

            autoplay_audio(
                st.session_state.audio_to_play
            )

        except Exception as e:

            print(
                "Audio playback error:",
                e
            )

    # =====================================================
    # COACH FEEDBACK
    # =====================================================

    if (
        workout_started
        and st.session_state.get(
            "coach_feedback"
        )
    ):

        st.success(
            f"🤖 Coach: "
            f"{st.session_state.coach_feedback}"
        )

    # =====================================================
    # PRE-WORKOUT
    # =====================================================

    if not workout_started:

        selected_exercise = st.session_state.get(
            "plan_exercise",
            EXERCISE_OPTIONS[0]
        )

        selected_sets = max(
            1,
            int(
                st.session_state.get(
                    "plan_sets",
                    3
                )
            )
        )

        selected_reps = max(
            1,
            int(
                st.session_state.get(
                    "plan_reps",
                    10
                )
            )
        )

        total_target = (
            selected_sets
            * selected_reps
        )

        # -------------------------------------------------
        # TODAY'S TRAINING
        # -------------------------------------------------

        st.subheader(
            "🏋️ Today's Training"
        )

        st.write(
            f"🏋️ Exercise: **{selected_exercise}**"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🎯 Sets",
                selected_sets
            )

        with col2:

            st.metric(
                "🔁 Reps / Set",
                selected_reps
            )

        with col3:

            st.metric(
                "📊 Total Target",
                total_target
            )

        st.divider()

        # -------------------------------------------------
        # AI COACH
        # -------------------------------------------------

        st.subheader(
            "🤖 Your AI Coach Will"
        )

        st.write(
            "🎯 Monitor your body position"
        )

        st.write(
            "🎙️ Give real-time voice corrections"
        )

        st.write(
            "📈 Track your reps and sets"
        )

        st.write(
            "💪 Analyze your workout performance"
        )

        st.info(
            "💡 Set your workout from the sidebar, "
            "then click **Start Workout** to activate "
            "your AI Coach."
        )

    # =====================================================
    # CAMERA / POSE DETECTION
    # =====================================================

    if workout_started:

        context = webrtc_streamer(

            key="exercise-analysis",

            mode=WebRtcMode.SENDRECV,

            video_processor_factory=VideoProcessorClass,

            rtc_configuration={
                "iceServers": [
                    {
                        "urls": [
                            "stun:stun.l.google.com:19302"
                        ]
                    }
                ]
            },

            media_stream_constraints={
                "video": True,
                "audio": False
            },

            async_processing=True
        )

        # -------------------------------------------------
        # SYNC LIVE METRICS
        # -------------------------------------------------

        try:

            sync_metrics_update(
                context
            )

        except Exception as e:

            print(
                "Metrics sync error:",
                e
            )

        # -------------------------------------------------
        # LIVE RERUN
        # -------------------------------------------------

        if context.state.playing:

            time.sleep(
                0.25
            )

            st.rerun()

        # -------------------------------------------------
        # WEBRTC STYLES
        # -------------------------------------------------

        inject_webrtc_styles()


# =========================================================
# APPLICATION
# =========================================================

def main():

    st.set_page_config(

        page_title="AI Real-time GYM Coach",

        page_icon="🏋️‍♀️",

        initial_sidebar_state="expanded",

        layout="centered"
    )

    # =====================================================
    # LOAD CSS
    # =====================================================

    load_css(
        os.path.join(
            STATIC_DIR,
            "style.css"
        )
    )

    # =====================================================
    # FONT
    # =====================================================

    inject_local_font(
        os.path.join(
            STATIC_DIR,
            "AdobeClean.otf"
        ),
        "AdobeClean"
    )

    # =====================================================
    # BACKGROUND
    # =====================================================

    set_background()

    # =====================================================
    # DATABASE
    # =====================================================

    init_db()

    # =====================================================
    # LOGIN
    # =====================================================

    if not render_login_wall():

        return

    # =====================================================
    # SESSION
    # =====================================================

    initial_session_defaults()

    ensure_session_defaults()

    # =====================================================
    # VOICE
    # =====================================================

    initialize_voice_pipeline()

    # =====================================================
    # SUMMARY PAGE
    # =====================================================

    if (
        st.session_state.get(
            "current_page"
        ) == "summary"
    ):

        render_workout_summary_page()

        return

    # =====================================================
    # SIDEBAR
    # =====================================================

    render_sidebar()

    # =====================================================
    # MAIN CONTENT
    # =====================================================

    render_main_page()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()