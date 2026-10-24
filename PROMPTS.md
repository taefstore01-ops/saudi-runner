# SAiFMaN — Prompts

## 1) Tripo: the SAiFMaN character

### Character prompt (Text to Image / Text to Model in Tripo)

```
Full-body 3D character of "SAiFMaN", a young Saudi superhero runner, stylized Pixar-like proportions,
standing in a neutral A-pose, arms slightly away from the body, feet shoulder-width apart, facing the camera.
Sleek royal-blue bodysuit with silver chrome panels on shoulders, forearms and shins, glossy chrome helmet
with a dark blue visor covering the eyes, a gold round emblem on the chest with a bold white letter "S",
gold belt, short red scarf around the neck, chrome running boots.
Clean simple shapes, no weapons, no cape, nothing held in the hands, plain white background,
soft studio lighting, full body visible from head to toe.
```

For better results: make 3 images (front, side, back) with the same description, adding at the end
`front view` / `side view, facing right` / `back view`, then use **Multi-view** in Tripo (same as Sadan).

### Steps in Tripo (same as Azzouz and Sadan)

1. Generate the model from the image(s) → pick the best one.
2. **Retopo** → 10k quads.
3. **Auto Rig** → Humanoid (Mixamo).
4. Animations: **run**, **idle**, **jump** (and **slide** if you can, via Text2Motion: "baseball slide on the ground, feet first").
5. Turn on **"stay in place"** (in place) for the animations.
6. **Export GLB** (2k textures + skeleton).
7. Put the file anywhere and tell me its path; I'll run:

```bash
python tools/wrap_model.py "path/saifman.glb"
```

The script shrinks the textures (to 1024) and writes `models/saifman.glb` and `models/saifman.js`,
and the game uses the model automatically instead of the placeholder character.

---

## 2) Google Stitch: the game screens and the Saudi cities

```
Design a mobile game UI (portrait, 390x844) for "SAiFMaN" (سيف مان), an Arabic endless-runner game
where a young Saudi superhero in a royal-blue suit with a chrome helmet and a gold "S" emblem runs
through the cities of Saudi Arabia, dodging obstacles and collecting blue energy cans.

Language & direction: all UI text in Arabic, full RTL layout. Fonts: "Lalezar" for titles and buttons,
"Cairo" for body text. The logo "SAiFMaN" stays in Latin letters with a gold dotted "i".

Visual style: bright, premium, cartoon-3D game art (Subway Surfers / Temple Run quality), glossy
buttons, rounded cards, soft shadows. Base palette: royal blue #1565FF, deep navy #071A4A,
gold #FFC531, red accent #FF3B4E, white. Each city adds its own accent color.

Screens to design:
1. Splash / title screen: big SAiFMaN logo, hero running toward the camera, Riyadh skyline behind.
2. Main lobby: hero showcase in the center, "ابدأ الجري" big gold button, coins/cans counter,
   best score, settings and shop icons.
3. City (world) picker: a swipeable carousel of 6 city cards, each with a large illustrated
   scene, the city name in Arabic, a short tagline, a lock icon + cans cost for locked cities:
   - الرياض (Riyadh): Kingdom Centre tower, Al Faisaliah, Masmak fortress mud walls, Diriyah
     At-Turaif Najdi architecture, palm trees, golden desert evening. Accent: sand gold.
   - جدة (Jeddah): Al-Balad historic coral-stone houses with wooden Roshan balconies, King Fahd's
     Fountain, Red Sea corniche, Jeddah Tower. Accent: sea turquoise.
   - الدمام (Dammam): Arabian Gulf corniche, modern waterfront, King Fahd Park, dhow boats,
     oil-heritage industrial touches, Gulf blue skies. Accent: gulf blue.
   - مكة المكرمة (Makkah): respectful scene of the city with the Makkah Clock Royal Tower and the
     surrounding mountains, illuminated at dusk, no people in prayer and no close-up of the Kaaba.
     Accent: emerald green and gold.
   - العلا (AlUla): Hegra (Mada'in Salih) Nabataean rock-cut tombs, Elephant Rock, Maraya mirrored
     building, red sandstone canyons, starry night. Accent: terracotta orange.
   - جازان (Jazan): green terraced mountains of Fifa, Farasan Islands beaches, mangroves,
     traditional Jazani huts (Al-Ushash), tropical fruit farms (mango, coffee). Accent: lush green.
4. In-game HUD: distance counter, cans counter, pause button, a small city badge, power-up slots.
5. Pause screen and Game-over screen: distance, cans, best score, "مرة ثانية" and "القائمة" buttons.
6. Character / shop screen: SAiFMaN skins (classic blue, desert gold, Jeddah sea, AlUla canyon).

Also produce, for each of the 6 cities, one wide environment scene (landscape, no UI) showing the
street a runner would run down: a straight road going into the distance, the city's landmarks and
architecture on both sides and on the horizon, game-art style, no text, no people.
```
