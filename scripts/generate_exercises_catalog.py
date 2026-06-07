"""Generate app/data/exercises.json with 120+ exercises."""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "app" / "data" / "exercises.json"

SIDE = "Film from the side with your entire body visible from head to feet."
FRONT = "Film from the front with your full body visible in frame."
SIDE_REPS = "Film from the side. Record 3–10 controlled reps with good lighting."

# (id, name, description, muscle_groups, filming_tip, available)
EXERCISES: list[tuple] = [
    # ── AI Form Coach MVP (available) ──────────────────────────────────────
    ("back_squat", "Back Squat", "A barbell squat with the bar across the upper back.", ["quadriceps", "glutes", "core"], SIDE_REPS, True),
    ("front_squat", "Front Squat", "A squat with the barbell held in the front rack position.", ["quadriceps", "glutes", "core"], SIDE_REPS, True),
    ("goblet_squat", "Goblet Squat", "A squat holding a dumbbell or kettlebell at chest height.", ["quadriceps", "glutes", "core"], SIDE_REPS, True),
    ("deadlift", "Deadlift", "A conventional barbell deadlift from the floor to lockout.", ["hamstrings", "glutes", "back", "core"], SIDE_REPS, True),
    ("romanian_deadlift", "Romanian Deadlift", "A hip-hinge deadlift with minimal knee bend.", ["hamstrings", "glutes", "back"], SIDE_REPS, True),
    ("sumo_deadlift", "Sumo Deadlift", "A wide-stance deadlift with hands inside the knees.", ["hamstrings", "glutes", "back"], SIDE_REPS, True),
    ("bench_press", "Bench Press", "A horizontal barbell press performed lying on a bench.", ["chest", "shoulders", "triceps"], "Film from the side at bench height with full body visible.", True),
    ("overhead_press", "Overhead Press", "A standing barbell press from shoulders to overhead.", ["shoulders", "triceps", "core"], SIDE_REPS, True),
    ("pull_up", "Pull-Up", "An overhand bodyweight pull from hang to chin over the bar.", ["lats", "biceps", "core"], "Film from the front or side; show full hang to chin-over-bar.", True),
    ("push_up", "Push-Up", "A bodyweight horizontal press from the floor.", ["chest", "triceps", "core"], SIDE_REPS, True),
    ("lunge", "Lunge", "A single-leg split stance with alternating legs.", ["quadriceps", "glutes"], SIDE_REPS, True),
    ("walking_lunge", "Walking Lunge", "Continuous forward lunges across the floor.", ["quadriceps", "glutes"], "Film from the side following the movement path.", True),
    ("bulgarian_split_squat", "Bulgarian Split Squat", "A rear-foot-elevated single-leg squat.", ["quadriceps", "glutes"], SIDE_REPS, True),
    ("hip_thrust", "Hip Thrust", "A barbell glute bridge with shoulders on a bench.", ["glutes", "hamstrings"], SIDE_REPS, True),
    ("kettlebell_swing", "Kettlebell Swing", "An explosive hip-driven kettlebell swing.", ["glutes", "hamstrings", "core"], SIDE_REPS, True),
    ("chin_up", "Chin-Up", "An underhand bodyweight pull to the bar.", ["lats", "biceps", "core"], "Film from the front or side with full range visible.", True),
    ("barbell_row", "Barbell Row", "A bent-over barbell row to the lower chest.", ["back", "biceps"], SIDE_REPS, True),
    ("dip", "Dip", "A bodyweight press on parallel bars or bench.", ["chest", "triceps", "shoulders"], SIDE_REPS, True),
    ("good_morning", "Good Morning", "A barbell hip hinge with the bar on the upper back.", ["hamstrings", "back", "glutes"], SIDE_REPS, True),
    ("step_up", "Step-Up", "A single-leg step onto a box or bench.", ["quadriceps", "glutes"], SIDE_REPS, True),
    # ── Squat variations (library) ─────────────────────────────────────────
    ("box_squat", "Box Squat", "A squat to a box before driving back up.", ["quadriceps", "glutes"], SIDE, False),
    ("pause_squat", "Pause Squat", "A squat with a pause at the bottom position.", ["quadriceps", "glutes"], SIDE, False),
    ("overhead_squat", "Overhead Squat", "A squat with the barbell held overhead.", ["quadriceps", "glutes", "shoulders"], SIDE, False),
    ("zercher_squat", "Zercher Squat", "A squat with the barbell held in the elbow crooks.", ["quadriceps", "glutes", "core"], SIDE, False),
    ("safety_bar_squat", "Safety Bar Squat", "A squat using a safety squat bar.", ["quadriceps", "glutes"], SIDE, False),
    ("hack_squat", "Hack Squat", "A machine-guided squat variation.", ["quadriceps", "glutes"], SIDE, False),
    ("bodyweight_squat", "Bodyweight Squat", "An air squat with no external load.", ["quadriceps", "glutes"], SIDE, False),
    ("jump_squat", "Jump Squat", "An explosive squat with a vertical jump.", ["quadriceps", "glutes"], SIDE, False),
    ("split_squat", "Split Squat", "A stationary lunge with both feet on the floor.", ["quadriceps", "glutes"], SIDE, False),
    ("reverse_lunge", "Reverse Lunge", "A lunge stepping backward.", ["quadriceps", "glutes"], SIDE, False),
    ("forward_lunge", "Forward Lunge", "A lunge stepping forward.", ["quadriceps", "glutes"], SIDE, False),
    ("lateral_lunge", "Lateral Lunge", "A side-step lunge.", ["quadriceps", "glutes"], FRONT, False),
    ("curtsy_lunge", "Curtsy Lunge", "A lunge crossing the rear leg behind.", ["quadriceps", "glutes"], FRONT, False),
    ("pistol_squat", "Pistol Squat", "A single-leg squat to full depth.", ["quadriceps", "glutes"], SIDE, False),
    ("cossack_squat", "Cossack Squat", "A deep lateral squat shifting side to side.", ["quadriceps", "glutes"], FRONT, False),
    ("anderson_squat", "Anderson Squat", "A squat starting from pins at the bottom.", ["quadriceps", "glutes"], SIDE, False),
    ("pin_squat", "Pin Squat", "A squat to pins at a set depth.", ["quadriceps", "glutes"], SIDE, False),
    ("tempo_squat", "Tempo Squat", "A squat with prescribed slow eccentric and concentric.", ["quadriceps", "glutes"], SIDE, False),
    ("belt_squat", "Belt Squat", "A squat loaded via a belt without spinal compression.", ["quadriceps", "glutes"], SIDE, False),
    ("sissy_squat", "Sissy Squat", "A quad-dominant squat leaning back with knees forward.", ["quadriceps"], SIDE, False),
    # ── Deadlift & hinge (library) ─────────────────────────────────────────
    ("conventional_deadlift", "Conventional Deadlift", "Standard hip-width stance deadlift.", ["hamstrings", "glutes", "back"], SIDE, False),
    ("stiff_leg_deadlift", "Stiff-Leg Deadlift", "A deadlift with minimal knee flexion throughout.", ["hamstrings", "back"], SIDE, False),
    ("trap_bar_deadlift", "Trap Bar Deadlift", "A deadlift using a hex/trap bar.", ["hamstrings", "glutes", "back"], SIDE, False),
    ("single_leg_romanian_deadlift", "Single-Leg Romanian Deadlift", "A one-leg RDL for balance and hamstring strength.", ["hamstrings", "glutes"], SIDE, False),
    ("deficit_deadlift", "Deficit Deadlift", "A deadlift standing on a platform for extra range.", ["hamstrings", "glutes", "back"], SIDE, False),
    ("block_pull", "Block Pull", "A deadlift from elevated blocks reducing range.", ["hamstrings", "glutes", "back"], SIDE, False),
    ("rack_pull", "Rack Pull", "A partial deadlift from knee height or above.", ["back", "glutes"], SIDE, False),
    ("snatch_grip_deadlift", "Snatch Grip Deadlift", "A deadlift with a wide snatch-width grip.", ["hamstrings", "glutes", "back"], SIDE, False),
    ("jefferson_deadlift", "Jefferson Deadlift", "A deadlift straddling the bar with mixed grip.", ["hamstrings", "glutes", "back"], FRONT, False),
    ("hyperextension", "Back Extension", "A hip extension on a GHD or bench.", ["hamstrings", "glutes", "back"], SIDE, False),
    ("reverse_hyperextension", "Reverse Hyperextension", "A reverse hyper on a dedicated machine.", ["glutes", "hamstrings"], SIDE, False),
    ("glute_bridge", "Glute Bridge", "A floor hip thrust without a bench.", ["glutes", "hamstrings"], SIDE, False),
    ("single_leg_hip_thrust", "Single-Leg Hip Thrust", "A hip thrust performed on one leg.", ["glutes", "hamstrings"], SIDE, False),
    ("nordic_hamstring_curl", "Nordic Hamstring Curl", "An eccentric hamstring curl from kneeling.", ["hamstrings"], SIDE, False),
    # ── Bench & chest ──────────────────────────────────────────────────────
    ("incline_bench_press", "Incline Bench Press", "A barbell press on an incline bench.", ["chest", "shoulders", "triceps"], SIDE, False),
    ("decline_bench_press", "Decline Bench Press", "A barbell press on a decline bench.", ["chest", "triceps"], SIDE, False),
    ("dumbbell_bench_press", "Dumbbell Bench Press", "A flat bench press with dumbbells.", ["chest", "shoulders", "triceps"], SIDE, False),
    ("incline_dumbbell_press", "Incline Dumbbell Press", "An incline press with dumbbells.", ["chest", "shoulders", "triceps"], SIDE, False),
    ("floor_press", "Floor Press", "A bench press performed lying on the floor.", ["chest", "triceps"], SIDE, False),
    ("close_grip_bench_press", "Close-Grip Bench Press", "A bench press with a narrow grip.", ["triceps", "chest"], SIDE, False),
    ("dumbbell_fly", "Dumbbell Fly", "A flat bench dumbbell fly.", ["chest"], SIDE, False),
    ("incline_dumbbell_fly", "Incline Dumbbell Fly", "An incline dumbbell fly.", ["chest"], SIDE, False),
    ("cable_fly", "Cable Fly", "A standing or seated cable chest fly.", ["chest"], FRONT, False),
    ("pec_deck", "Pec Deck", "A machine chest fly.", ["chest"], FRONT, False),
    ("push_up_diamond", "Diamond Push-Up", "A push-up with hands forming a diamond.", ["triceps", "chest"], SIDE, False),
    ("decline_push_up", "Decline Push-Up", "A push-up with feet elevated.", ["chest", "shoulders"], SIDE, False),
    ("archer_push_up", "Archer Push-Up", "A wide push-up shifting weight to one arm.", ["chest", "triceps"], FRONT, False),
    ("chest_press_machine", "Chest Press Machine", "A seated machine horizontal press.", ["chest", "triceps"], SIDE, False),
    ("landmine_press", "Landmine Press", "A half-kneeling or standing landmine press.", ["chest", "shoulders"], SIDE, False),
    # ── Shoulders ──────────────────────────────────────────────────────────
    ("dumbbell_shoulder_press", "Dumbbell Shoulder Press", "A seated or standing dumbbell overhead press.", ["shoulders", "triceps"], SIDE, False),
    ("push_press", "Push Press", "An overhead press using leg drive.", ["shoulders", "triceps", "legs"], SIDE, False),
    ("arnold_press", "Arnold Press", "A rotating dumbbell overhead press.", ["shoulders", "triceps"], SIDE, False),
    ("lateral_raise", "Lateral Raise", "A dumbbell raise to the side.", ["shoulders"], FRONT, False),
    ("front_raise", "Front Raise", "A dumbbell raise to the front.", ["shoulders"], SIDE, False),
    ("rear_delt_fly", "Rear Delt Fly", "A bent-over rear deltoid fly.", ["shoulders", "back"], SIDE, False),
    ("face_pull", "Face Pull", "A cable pull to the face with external rotation.", ["shoulders", "back"], FRONT, False),
    ("upright_row", "Upright Row", "A vertical pull with a narrow grip.", ["shoulders", "traps"], FRONT, False),
    ("shrug", "Shrug", "A vertical trap shrug with dumbbells or barbell.", ["traps"], FRONT, False),
    ("cable_lateral_raise", "Cable Lateral Raise", "A lateral raise using a cable.", ["shoulders"], FRONT, False),
    ("machine_shoulder_press", "Machine Shoulder Press", "A seated machine overhead press.", ["shoulders", "triceps"], SIDE, False),
    ("pike_push_up", "Pike Push-Up", "A push-up in pike position targeting shoulders.", ["shoulders", "triceps"], SIDE, False),
    ("handstand_push_up", "Handstand Push-Up", "An inverted vertical bodyweight press.", ["shoulders", "triceps"], SIDE, False),
    # ── Back & lats ─────────────────────────────────────────────────────────
    ("dumbbell_row", "Dumbbell Row", "A single-arm or two-arm dumbbell row.", ["back", "biceps"], SIDE, False),
    ("pendlay_row", "Pendlay Row", "A strict bent-over barbell row from the floor.", ["back", "biceps"], SIDE, False),
    ("t_bar_row", "T-Bar Row", "A row using a landmine or T-bar setup.", ["back", "biceps"], SIDE, False),
    ("seated_cable_row", "Seated Cable Row", "A seated horizontal cable row.", ["back", "biceps"], SIDE, False),
    ("chest_supported_row", "Chest-Supported Row", "An incline bench supported dumbbell row.", ["back", "biceps"], SIDE, False),
    ("lat_pulldown", "Lat Pulldown", "A seated cable pulldown to the chest.", ["lats", "biceps"], FRONT, False),
    ("pull_over", "Pullover", "A dumbbell or cable pullover across the chest.", ["lats", "chest"], SIDE, False),
    ("straight_arm_pulldown", "Straight-Arm Pulldown", "A lat isolation with straight arms.", ["lats"], FRONT, False),
    ("inverted_row", "Inverted Row", "A bodyweight horizontal row under a bar.", ["back", "biceps"], SIDE, False),
    ("meadows_row", "Meadows Row", "A single-arm landmine row.", ["back", "biceps"], SIDE, False),
    ("machine_row", "Machine Row", "A seated machine horizontal row.", ["back", "biceps"], SIDE, False),
    ("assisted_pull_up", "Assisted Pull-Up", "A pull-up with counterweight assistance.", ["lats", "biceps"], FRONT, False),
    ("muscle_up", "Muscle-Up", "A pull-up transitioning to a dip over the bar.", ["lats", "chest", "triceps"], FRONT, False),
    # ── Arms ────────────────────────────────────────────────────────────────
    ("barbell_curl", "Barbell Curl", "A standing barbell bicep curl.", ["biceps"], FRONT, False),
    ("dumbbell_curl", "Dumbbell Curl", "A standing alternating dumbbell curl.", ["biceps"], FRONT, False),
    ("hammer_curl", "Hammer Curl", "A neutral-grip dumbbell curl.", ["biceps", "forearms"], FRONT, False),
    ("preacher_curl", "Preacher Curl", "A curl with arms supported on a preacher bench.", ["biceps"], SIDE, False),
    ("concentration_curl", "Concentration Curl", "A seated single-arm curl.", ["biceps"], FRONT, False),
    ("cable_curl", "Cable Curl", "A bicep curl using a cable stack.", ["biceps"], FRONT, False),
    ("tricep_pushdown", "Tricep Pushdown", "A cable pushdown for triceps.", ["triceps"], FRONT, False),
    ("skull_crusher", "Skull Crusher", "A lying tricep extension.", ["triceps"], SIDE, False),
    ("overhead_tricep_extension", "Overhead Tricep Extension", "A dumbbell or cable overhead tricep extension.", ["triceps"], SIDE, False),
    ("tricep_dip", "Tricep Dip", "A dip emphasizing upright torso for triceps.", ["triceps"], SIDE, False),
    ("bench_dip", "Bench Dip", "A dip between two benches.", ["triceps"], SIDE, False),
    ("close_grip_push_up", "Close-Grip Push-Up", "A push-up with hands close together.", ["triceps", "chest"], SIDE, False),
    ("wrist_curl", "Wrist Curl", "A forearm flexion curl.", ["forearms"], FRONT, False),
    ("reverse_wrist_curl", "Reverse Wrist Curl", "A forearm extension curl.", ["forearms"], FRONT, False),
    # ── Legs & glutes ───────────────────────────────────────────────────────
    ("leg_press", "Leg Press", "A machine leg press.", ["quadriceps", "glutes"], SIDE, False),
    ("leg_extension", "Leg Extension", "A seated quadriceps extension machine.", ["quadriceps"], SIDE, False),
    ("leg_curl", "Leg Curl", "A lying or seated hamstring curl machine.", ["hamstrings"], SIDE, False),
    ("calf_raise", "Calf Raise", "A standing calf raise.", ["calves"], SIDE, False),
    ("seated_calf_raise", "Seated Calf Raise", "A seated calf raise.", ["calves"], SIDE, False),
    ("hip_abduction", "Hip Abduction", "A machine or band hip abduction.", ["glutes"], FRONT, False),
    ("hip_adduction", "Hip Adduction", "A machine hip adduction.", ["glutes"], FRONT, False),
    ("glute_kickback", "Glute Kickback", "A cable or machine glute kickback.", ["glutes"], SIDE, False),
    ("donkey_kick", "Donkey Kick", "A quadruped hip extension.", ["glutes"], SIDE, False),
    ("fire_hydrant", "Fire Hydrant", "A quadruped hip abduction.", ["glutes"], SIDE, False),
    ("wall_sit", "Wall Sit", "An isometric squat against a wall.", ["quadriceps"], SIDE, False),
    ("goblet_lateral_lunge", "Goblet Lateral Lunge", "A lateral lunge holding a kettlebell.", ["quadriceps", "glutes"], FRONT, False),
    # ── Core ────────────────────────────────────────────────────────────────
    ("plank", "Plank", "An isometric front plank hold.", ["core"], SIDE, False),
    ("side_plank", "Side Plank", "An isometric side plank hold.", ["core"], FRONT, False),
    ("sit_up", "Sit-Up", "A full sit-up from the floor.", ["core"], SIDE, False),
    ("crunch", "Crunch", "An abdominal crunch.", ["core"], SIDE, False),
    ("bicycle_crunch", "Bicycle Crunch", "A rotational alternating crunch.", ["core"], FRONT, False),
    ("hanging_leg_raise", "Hanging Leg Raise", "A leg raise from a pull-up bar.", ["core"], SIDE, False),
    ("lying_leg_raise", "Lying Leg Raise", "A supine leg raise.", ["core"], SIDE, False),
    ("russian_twist", "Russian Twist", "A seated rotational core exercise.", ["core"], FRONT, False),
    ("dead_bug", "Dead Bug", "A supine anti-extension core drill.", ["core"], FRONT, False),
    ("bird_dog", "Bird Dog", "A quadruped opposite arm and leg extension.", ["core"], SIDE, False),
    ("pallof_press", "Pallof Press", "An anti-rotation cable press.", ["core"], FRONT, False),
    ("ab_wheel_rollout", "Ab Wheel Rollout", "An ab wheel rollout from kneeling.", ["core"], SIDE, False),
    ("mountain_climber", "Mountain Climber", "A dynamic plank knee drive.", ["core"], SIDE, False),
    ("v_up", "V-Up", "A simultaneous upper and lower body crunch.", ["core"], SIDE, False),
    ("cable_crunch", "Cable Crunch", "A kneeling cable crunch.", ["core"], SIDE, False),
    # ── Olympic & power ─────────────────────────────────────────────────────
    ("power_clean", "Power Clean", "An explosive barbell clean to the shoulders.", ["full body"], SIDE, False),
    ("hang_clean", "Hang Clean", "A clean starting from the hang position.", ["full body"], SIDE, False),
    ("clean_and_jerk", "Clean and Jerk", "An Olympic lift combining clean and jerk.", ["full body"], SIDE, False),
    ("snatch", "Snatch", "An Olympic barbell snatch to overhead.", ["full body"], SIDE, False),
    ("power_snatch", "Power Snatch", "A snatch caught in a partial squat.", ["full body"], SIDE, False),
    ("push_jerk", "Push Jerk", "A jerk using leg drive and a quick dip.", ["shoulders", "legs"], SIDE, False),
    ("split_jerk", "Split Jerk", "A jerk caught in a split stance.", ["shoulders", "legs"], SIDE, False),
    ("clean_pull", "Clean Pull", "The pull phase of the clean without the catch.", ["full body"], SIDE, False),
    ("snatch_pull", "Snatch Pull", "The pull phase of the snatch without the catch.", ["full body"], SIDE, False),
    # ── Kettlebell ──────────────────────────────────────────────────────────
    ("kettlebell_goblet_squat", "Kettlebell Goblet Squat", "A goblet squat with a kettlebell.", ["quadriceps", "glutes"], SIDE, False),
    ("kettlebell_clean", "Kettlebell Clean", "A single-arm kettlebell clean.", ["full body"], SIDE, False),
    ("kettlebell_snatch", "Kettlebell Snatch", "A single-arm kettlebell snatch.", ["full body"], SIDE, False),
    ("kettlebell_press", "Kettlebell Press", "A single-arm kettlebell overhead press.", ["shoulders"], SIDE, False),
    ("kettlebell_turkish_get_up", "Turkish Get-Up", "A full-body get-up from the floor to standing.", ["full body"], SIDE, False),
    ("kettlebell_windmill", "Kettlebell Windmill", "A lateral hip hinge with KB overhead.", ["core", "shoulders"], FRONT, False),
    # ── Calisthenics & conditioning ────────────────────────────────────────
    ("burpee", "Burpee", "A full-body conditioning movement.", ["full body"], SIDE, False),
    ("box_jump", "Box Jump", "A plyometric jump onto a box.", ["legs"], SIDE, False),
    ("broad_jump", "Broad Jump", "A horizontal standing long jump.", ["legs"], SIDE, False),
    ("jumping_jack", "Jumping Jack", "A basic jumping jack.", ["full body"], FRONT, False),
    ("high_knees", "High Knees", "Running in place with high knee drive.", ["legs", "core"], FRONT, False),
    ("bear_crawl", "Bear Crawl", "A quadruped crawl on hands and feet.", ["core", "shoulders"], SIDE, False),
    ("crab_walk", "Crab Walk", "A reverse tabletop crawl.", ["shoulders", "triceps"], FRONT, False),
    ("l_sit", "L-Sit", "An isometric hold with legs extended.", ["core"], SIDE, False),
    ("hollow_body_hold", "Hollow Body Hold", "A supine isometric core hold.", ["core"], SIDE, False),
    ("superman_hold", "Superman Hold", "A prone back extension hold.", ["back", "glutes"], SIDE, False),
    # ── Mobility ────────────────────────────────────────────────────────────
    ("worlds_greatest_stretch", "World's Greatest Stretch", "A lunge with thoracic rotation.", ["mobility"], SIDE, False),
    ("cat_cow", "Cat-Cow", "A spinal flexion and extension flow.", ["mobility"], SIDE, False),
    ("hip_flexor_stretch", "Hip Flexor Stretch", "A half-kneeling hip flexor stretch.", ["mobility"], SIDE, False),
    ("hamstring_stretch", "Hamstring Stretch", "A standing or seated hamstring stretch.", ["mobility"], SIDE, False),
    ("shoulder_dislocates", "Shoulder Dislocates", "A band pass-through for shoulder mobility.", ["mobility"], FRONT, False),
    ("ankle_mobilization", "Ankle Mobilization", "A knee-over-toe ankle mobility drill.", ["mobility"], SIDE, False),
    # ── Carries & misc ──────────────────────────────────────────────────────
    ("farmer_walk", "Farmer Walk", "A loaded carry with dumbbells or kettlebells.", ["core", "traps"], SIDE, False),
    ("suitcase_carry", "Suitcase Carry", "A single-arm loaded carry.", ["core"], SIDE, False),
    ("overhead_carry", "Overhead Carry", "A walk with weight held overhead.", ["shoulders", "core"], SIDE, False),
    ("sled_push", "Sled Push", "A horizontal sled push.", ["legs"], SIDE, False),
    ("sled_pull", "Sled Pull", "A backward sled drag.", ["legs"], FRONT, False),
    ("battle_ropes", "Battle Ropes", "Alternating or slamming rope waves.", ["shoulders", "core"], FRONT, False),
    ("medicine_ball_slam", "Medicine Ball Slam", "An overhead slam to the floor.", ["core", "shoulders"], FRONT, False),
    ("medicine_ball_throw", "Medicine Ball Throw", "A chest or overhead med ball throw.", ["chest", "core"], SIDE, False),
    ("jump_rope", "Jump Rope", "Basic jump rope skipping.", ["calves"], FRONT, False),
    ("rower", "Rowing Machine", "A cardio row on a Concept2-style erg.", ["full body"], SIDE, False),
    ("assault_bike", "Assault Bike", "An air bike sprint.", ["full body"], FRONT, False),
]


def main() -> None:
    exercises = [
        {
            "id": eid,
            "name": name,
            "description": desc,
            "muscle_groups": groups,
            "filming_tip": tip,
            "available": available,
        }
        for eid, name, desc, groups, tip, available in EXERCISES
    ]

    ids = [e["id"] for e in exercises]
    assert len(ids) == len(set(ids)), "Duplicate exercise ids found"
    assert len(exercises) >= 120, f"Expected 120+ exercises, got {len(exercises)}"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps({"exercises": exercises}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    available_count = sum(1 for e in exercises if e["available"])
    print(f"Wrote {len(exercises)} exercises ({available_count} coach-enabled) to {OUTPUT}")


if __name__ == "__main__":
    main()
