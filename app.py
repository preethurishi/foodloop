import streamlit as st
import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime

# Page configuration must be the first Streamlit command.
st.set_page_config(
    page_title="FoodLoop | Save Food, Feed People",
    page_icon="🌱",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGOS_DIR = ASSETS_DIR / "logos"
IMAGES_DIR = ASSETS_DIR / "images"
DATA_DIR = BASE_DIR / "data"
CSV_FILE = DATA_DIR / "donations.csv"
DATA_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "id", "donor", "food", "quantity", "location",
    "prepared_time", "pickup_deadline", "notes", "status"
]


# -------------------- CSV storage --------------------
def load_donations():
    """Load donations and normalize columns from earlier app versions."""
    if not CSV_FILE.exists():
        return pd.DataFrame(columns=COLUMNS)

    try:
        df = pd.read_csv(CSV_FILE, dtype={"id": str})
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)

    # Backward compatibility with the previous field names.
    df = df.rename(columns={
        "prepared": "prepared_time",
        "deadline": "pickup_deadline",
    })

    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[COLUMNS].fillna("")
    missing_ids = df["id"].astype(str).str.strip().eq("")
    if missing_ids.any():
        df.loc[missing_ids, "id"] = [
            str(uuid.uuid4()) for _ in range(int(missing_ids.sum()))
        ]
        df.to_csv(CSV_FILE, index=False)

    return df


def save_donation(donation):
    df = load_donations()
    df = pd.concat(
        [df, pd.DataFrame([donation], columns=COLUMNS)],
        ignore_index=True,
    )
    df.to_csv(CSV_FILE, index=False)


def update_status(donation_id, new_status):
    df = load_donations()
    df.loc[df["id"].astype(str) == str(donation_id), "status"] = new_status
    df.to_csv(CSV_FILE, index=False)


if not CSV_FILE.exists():
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)


# -------------------- Styling --------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #F7F9F4; color: #24352B; }
    .stApp p, .stApp li, .stApp label { color: #24352B; }
    h1, h2, h3, h4 { color: #174D35 !important; font-weight: 700 !important; }
    .main-title {
        font-size: clamp(38px, 5vw, 54px);
        font-weight: 800; color: #176B45; line-height: 1.1;
    }
    .subtitle { font-size: 19px; color: #405B4A; margin-bottom: 12px; }
    [data-testid="stSidebar"] { background-color: #E6EFE5; }
    [data-testid="stSidebar"] * { color: #174D35; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        color: #172B20 !important; background-color: #FFFFFF !important;
        -webkit-text-fill-color: #172B20 !important;
        border: 1px solid #A7B9A9 !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #68776D !important; -webkit-text-fill-color: #68776D !important;
        opacity: 1 !important;
    }
    [data-testid="stWidgetLabel"] p { color: #174D35 !important; font-weight: 600 !important; }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #176B45 !important; color: #FFFFFF !important;
        border-radius: 10px; border: none; padding: 10px 18px; font-weight: 700;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #0F5032 !important; color: #FFFFFF !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #C9D9CA; border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- Partner logos --------------------
logo_items = [
    (LOGOS_DIR / "rit_logo.jpg", "Rajeev Institute of Technology"),
    (LOGOS_DIR / "cse_logo.jpg", "Department of Computer Science"),
    (LOGOS_DIR / "gdg_logo.jpg", "GDG on Campus – RIT Hassan"),
]
logo_cols = st.columns(3)
for col, (logo_path, label) in zip(logo_cols, logo_items):
    with col:
        if logo_path.exists():
            st.image(str(logo_path), width=140)
            st.caption(label)
        else:
            st.warning(f"Logo not found: {logo_path.name}")


# -------------------- Navigation --------------------
PAGES = ["Home", "Donate Food", "Find Food", "Impact Dashboard", "About Us"]


def go_to(page_name):
    st.session_state["page"] = page_name


if "page" not in st.session_state:
    st.session_state["page"] = "Home"

st.sidebar.title("🌱 FoodLoop")
st.sidebar.caption("Save Food. Feed People.")
st.sidebar.radio("Navigation", PAGES, key="page")
page = st.session_state["page"]


# -------------------- Home --------------------
if page == "Home":
    st.markdown('<div class="main-title">🌱 FoodLoop</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Save Food. Feed People. Build a Better Tomorrow.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #064e3b, #047857);
            padding: 22px 28px; border-radius: 14px; color: white;
            font-size: 20px; font-weight: 600; text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            margin: 15px 0 25px 0;
        ">
            🌱 Together, we can turn surplus food into hope.
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_path = IMAGES_DIR / "foodloop_hero.jpg"
    if hero_path.exists():
        st.image(str(hero_path), use_container_width=True)
    else:
        st.info("Place your hero image at assets/images/foodloop_hero.jpg.")

    st.markdown("## Every Meal Deserves a Purpose ❤️")
    st.write(
        "FoodLoop connects restaurants, hotels, supermarkets and event "
        "organizers with NGOs and communities to redistribute surplus "
        "food and reduce food waste."
    )

    button1, button2 = st.columns(2)
    with button1:
        st.button(
            "🍱 Donate Surplus Food", on_click=go_to,
            args=("Donate Food",), use_container_width=True,
        )
    with button2:
        st.button(
            "🔎 Find Available Food", on_click=go_to,
            args=("Find Food",), use_container_width=True,
        )

    st.markdown("---")
    st.markdown("## How FoodLoop Works")
    step1, step2, step3 = st.columns(3)
    with step1:
        st.markdown("### 🍱 1. Donate")
        st.write("Restaurants and individuals list surplus food.")
    with step2:
        st.markdown("### 🤝 2. Connect")
        st.write("NGOs and volunteers discover available donations.")
    with step3:
        st.markdown("### ❤️ 3. Deliver")
        st.write("Food is collected and shared with people who need it.")

    st.markdown("---")
    st.markdown("### Our Mission")
    st.write(
        "Reduce food waste, support communities and build a world "
        "where good food does not go to waste."
    )


# -------------------- Donate Food --------------------
elif page == "Donate Food":
    st.title("🍱 Donate Surplus Food")
    st.write(
        "Share available surplus food with NGOs, volunteers and "
        "communities who need it."
    )

    with st.form("donation_form", clear_on_submit=True):
        donor = st.text_input("Restaurant / Donor Name *")
        food = st.text_input("Food Name *")
        quantity = st.number_input(
            "Number of Meals *", min_value=1, max_value=100000,
            value=1, step=1,
        )
        location = st.text_input("Pickup Location *")

        st.subheader("Preparation and Pickup Details")
        prepared = st.text_input(
            "Food Preparation Time (HH:MM) *", placeholder="Example: 11:30"
        )
        deadline = st.text_input(
            "Safe Pickup Deadline (HH:MM) *", placeholder="Example: 14:00"
        )
        notes = st.text_area(
            "Storage Conditions, Allergens and Additional Details",
            placeholder=(
                "Example: Vegetarian food. Keep covered. "
                "Contains dairy. Keep refrigerated."
            ),
            height=130,
        )
        st.caption(
            "Use 24-hour time. Example: 09:30 for 9:30 AM and "
            "14:30 for 2:30 PM."
        )
        submitted = st.form_submit_button(
            "🍱 Submit Donation", use_container_width=True
        )

    if submitted:
        if not donor.strip() or not food.strip() or not location.strip():
            st.error("Please complete Donor Name, Food Name and Pickup Location.")
        elif not prepared.strip() or not deadline.strip():
            st.error("Please enter both preparation time and pickup deadline.")
        else:
            try:
                prepared_dt = datetime.strptime(prepared.strip(), "%H:%M")
                deadline_dt = datetime.strptime(deadline.strip(), "%H:%M")
            except ValueError:
                st.error("Enter times in HH:MM format, for example 09:30.")
            else:
                if deadline_dt <= prepared_dt:
                    st.error(
                        "Pickup deadline must be later than preparation "
                        "time on the same day."
                    )
                else:
                    donation = {
                        "id": str(uuid.uuid4()),
                        "donor": donor.strip(),
                        "food": food.strip(),
                        "quantity": int(quantity),
                        "location": location.strip(),
                        "prepared_time": prepared.strip(),
                        "pickup_deadline": deadline.strip(),
                        "notes": notes.strip(),
                        "status": "Available",
                    }
                    save_donation(donation)
                    st.success("🎉 Donation successfully added to FoodLoop!")
                    st.info(
                        "Your donation is now listed on Find Food for "
                        "NGOs and volunteers to discover."
                    )


# -------------------- Find Food --------------------
elif page == "Find Food":
    st.title("🔎 Discover Available Food")
    st.write("Explore surplus food donations shared by our community.")

    donations = load_donations()
    available = donations[donations["status"] == "Available"].copy()
    search = st.text_input(
        "Search food or pickup location",
        placeholder="Search by food name or location...",
    )

    if search.strip():
        food_match = available["food"].astype(str).str.contains(
            search.strip(), case=False, na=False
        )
        location_match = available["location"].astype(str).str.contains(
            search.strip(), case=False, na=False
        )
        available = available[food_match | location_match]

    if available.empty:
        st.info("No matching available donations found. Please check back later.")
    else:
        st.write(f"### {len(available)} Available Donation(s)")
        for _, item in available.iterrows():
            with st.container(border=True):
                st.subheader(f"🍲 {item['food']}")
                left, right = st.columns(2)
                with left:
                    st.write(f"**Donor:** {item['donor']}")
                    st.write(f"**Meals available:** {item['quantity']}")
                    st.write(f"**Pickup location:** {item['location']}")
                with right:
                    st.write(f"**Prepared at:** {item['prepared_time']}")
                    st.write(f"**Pickup deadline:** {item['pickup_deadline']}")
                    st.write(f"**Status:** {item['status']}")

                st.markdown("**Storage Conditions and Allergens**")
                st.write(
                    item["notes"] if str(item["notes"]).strip()
                    else "Not provided."
                )
                st.caption(
                    "Confirm food condition, storage and safe handling "
                    "before collection."
                )

                if st.button(
                    "Reserve Food", key=f"reserve_{item['id']}"
                ):
                    update_status(item["id"], "Reserved")
                    st.success("Food reservation recorded successfully!")
                    st.rerun()


# -------------------- Impact Dashboard --------------------
elif page == "Impact Dashboard":
    st.title("📊 FoodLoop Impact Dashboard")
    st.write("See how our community is helping reduce food waste.")

    donations = load_donations()
    total_donations = len(donations)

    if total_donations:
        total_meals = int(
            pd.to_numeric(donations["quantity"], errors="coerce")
            .fillna(0).sum()
        )
        reserved_count = int((donations["status"] == "Reserved").sum())
        available_count = int((donations["status"] == "Available").sum())
    else:
        total_meals = 0
        reserved_count = 0
        available_count = 0

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Total Meals Listed", total_meals)
    metric2.metric("Food Donations", total_donations)
    metric3.metric("Reserved Donations", reserved_count)

    st.markdown("---")
    st.subheader("Donation Status")
    st.write(f"Available donations: {available_count}")
    st.write(f"Reserved donations: {reserved_count}")

    if total_donations:
        chart_data = donations.copy()
        chart_data["quantity"] = pd.to_numeric(
            chart_data["quantity"], errors="coerce"
        ).fillna(0)
        st.bar_chart(chart_data.groupby("status")["quantity"].sum())
    else:
        st.info("Donation statistics will appear here after the first donation.")


# -------------------- About Us --------------------
elif page == "About Us":
    st.title("🌍 About FoodLoop")
    st.write(
        "FoodLoop is a community-driven platform designed to connect "
        "food donors with NGOs and volunteers."
    )
    st.markdown("### Our Vision")
    st.write("A world where surplus food feeds people instead of becoming waste.")
    st.markdown("### Our Mission")
    st.write(
        "To reduce food waste and make surplus food accessible to "
        "communities in need."
    )
    st.markdown("### Our Values")
    st.write("- Sustainability")
    st.write("- Community support")
    st.write("- Food safety")
    st.write("- Transparency")


# -------------------- Footer --------------------
st.markdown("---")
st.caption("© 2026 FoodLoop | Save Food. Feed People. 🌱")
