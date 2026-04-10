
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from faker import Faker

fake = Faker("ru_RU")
rng  = np.random.default_rng(42)

DISTRICTS = [
    ("Советский",       "Центр / Кремль",           1.35),
    ("Советский",       "Лесопарк / Борки",          1.20),
    ("Советский",       "Кальное",                   1.05),
    ("Советский",       "Солотча",                   1.10),
    ("Советский",       "Бутырки",                   0.95),
    ("Московский",      "Московский",                1.15),
    ("Московский",      "Приокский",                 1.10),
    ("Московский",      "Канищево",                  1.05),
    ("Московский",      "Юбилейный",                 1.08),
    ("Московский",      "Красный",                   1.00),
    ("Московский",      "Дягилево",                  0.92),
    ("Московский",      "Мервино",                   0.88),
    ("Московский",      "Недостоево",                0.85),
    ("Октябрьский",     "Дашково-Песочня",           1.00),
    ("Октябрьский",     "Центральный",               1.12),
    ("Октябрьский",     "Шереметьево-Песочня",       0.93),
    ("Октябрьский",     "Мирный",                    0.90),
    ("Октябрьский",     "Голенчино",                 0.78),
    ("Октябрьский",     "Никуличи",                  0.75),
    ("Октябрьский",     "Строитель",                 0.80),
    ("Железнодорожный", "Горроща",                   0.95),
    ("Железнодорожный", "Октябрьский городок",       0.88),
    ("Железнодорожный", "Ленпоселок",                0.85),
    ("Железнодорожный", "Южный",                     0.82),
    ("Железнодорожный", "Михайловское шоссе",        0.78),
    ("Железнодорожный", "Мехзавод / Храпово",        0.72),
]

BASE_PRICE  = 97_000
N_ROWS      = 1_500

admin_list = [d[0] for d in DISTRICTS]
nbhd_list  = [d[1] for d in DISTRICTS]
coef_list  = [d[2] for d in DISTRICTS]

weights = np.array(coef_list) / sum(coef_list)
idx = rng.choice(len(DISTRICTS), size=N_ROWS, p=weights)

records = []

HOUSE_TYPES  = ["панель", "монолит", "кирпич", "блок"]
HOUSE_PROBS  = [0.40, 0.25, 0.25, 0.10]
RENOV_TYPES  = ["без ремонта", "косметический", "евроремонт", "дизайнерский"]
RENOV_PROBS  = [0.20, 0.45, 0.28, 0.07]
RENOV_MULT   = {"без ремонта": 0.90, "косметический": 1.00,
                "евроремонт": 1.10, "дизайнерский": 1.20}
HOUSE_MULT   = {"панель": 0.95, "монолит": 1.05, "кирпич": 1.03, "блок": 0.97}
FLOORS_POOL  = [5, 9, 10, 12, 16, 17, 25]
FLOORS_PROBS = [0.20, 0.20, 0.10, 0.15, 0.20, 0.10, 0.05]

for i in range(N_ROWS):
    d_idx = idx[i]
    admin  = admin_list[d_idx]
    nbhd   = nbhd_list[d_idx]
    coef   = coef_list[d_idx]

    street    = fake.street_name()          # улица
    house_num = fake.building_number()      # номер дома

    area        = round(float(np.clip(rng.lognormal(3.85, 0.45), 20, 150)), 1)
    total_floors = int(rng.choice(FLOORS_POOL, p=FLOORS_PROBS))
    floor        = int(rng.integers(1, total_floors + 1))
    year_built   = int(rng.integers(1960, 2025))
    dist_center  = round(float(np.clip(
                       rng.normal((1.35 - coef) * 12 + 2, 1.5), 0.5, 25)), 1)

    if area < 35:
        rooms = 1
    elif area < 60:
        rooms = int(rng.choice([1, 2], p=[0.3, 0.7]))
    elif area < 90:
        rooms = int(rng.choice([2, 3], p=[0.4, 0.6]))
    else:
        rooms = int(rng.choice([3, 4], p=[0.6, 0.4]))

    house_type  = str(rng.choice(HOUSE_TYPES, p=HOUSE_PROBS))
    renovation  = str(rng.choice(RENOV_TYPES, p=RENOV_PROBS))
    has_parking = int(rng.choice([0, 1], p=[0.55, 0.45]))
    has_balcony = int(rng.choice([0, 1], p=[0.30, 0.70]))

    floor_mult = 0.96 if floor == 1 else (0.97 if floor == total_floors else 1.00)

    price_per_m2 = int(
        BASE_PRICE
        * coef
        * RENOV_MULT[renovation]
        * HOUSE_MULT[house_type]
        * floor_mult
        * (1 + has_parking * 0.03)
        * (1 + has_balcony * 0.02)
        * float(rng.uniform(0.95, 1.05))
    )
    price_total = round(price_per_m2 * area / 1000) * 1000  # до тысяч

    records.append({
        "id":                          i + 1,
        "адрес":                       f"г. Рязань, ул. {street}, д. {house_num}",
        "административный_район":      admin,
        "микрорайон":                  nbhd,
        "площадь_м2":                  area,
        "комнат":                      rooms,
        "этаж":                        floor,
        "этажей_в_доме":               total_floors,
        "тип_дома":                    house_type,
        "год_постройки":               year_built,
        "удаленность_от_центра_км":    dist_center,
        "парковка":                    has_parking,
        "балкон":                      has_balcony,
        "ремонт":                      renovation,
        "цена_за_м2":                  price_per_m2,
        "цена_руб":                    int(price_total),
    })

df = pd.DataFrame(records)
df.to_csv("ryazan_real_estate.csv", index=False, encoding="utf-8-sig", decimal=",")
print(f"✅ Датасет: {len(df)} строк, {df.shape[1]} признаков")
print(df[["площадь_м2", "комнат", "цена_за_м2", "цена_руб"]].describe().round(0))


fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("EDA — Недвижимость Рязани (Faker + numpy)", fontsize=15, fontweight="bold")

# 1. Гистограмма цен
axes[0, 0].hist(df["цена_руб"] / 1e6, bins=40, color="#4C72B0", edgecolor="white")
axes[0, 0].set_title("Распределение цен")
axes[0, 0].set_xlabel("Цена, млн руб.")
axes[0, 0].set_ylabel("Количество")

# 2. Boxplot по районам
order = df.groupby("административный_район")["цена_за_м2"].median().sort_values(ascending=False).index
data_box = [df[df["административный_район"] == d]["цена_за_м2"].values for d in order]
axes[0, 1].boxplot(data_box, tick_labels=order)
axes[0, 1].set_title("Цена/м² по районам")
axes[0, 1].set_ylabel("Цена за м², руб.")
plt.sca(axes[0, 1]); plt.xticks(rotation=20, ha="right")

# 3. Scatter площадь vs цена
sc = axes[0, 2].scatter(df["площадь_м2"], df["цена_руб"] / 1e6,
                         alpha=0.3, s=10, c=df["цена_за_м2"], cmap="RdYlGn")
axes[0, 2].set_title("Площадь vs Цена")
axes[0, 2].set_xlabel("Площадь, м²"); axes[0, 2].set_ylabel("Цена, млн руб.")
plt.colorbar(sc, ax=axes[0, 2], label="Цена/м²")

# 4. Топ-15 микрорайонов
top_nb = df.groupby("микрорайон")["цена_за_м2"].mean().sort_values().tail(15)
top_nb.plot(kind="barh", ax=axes[1, 0], color="#55A868")
axes[1, 0].set_title("Средняя цена/м² — топ-15 микрорайонов")
axes[1, 0].set_xlabel("Руб./м²")

# 5. Количество по районам
df["административный_район"].value_counts().plot(
    kind="bar", ax=axes[1, 1], color="#C44E52", edgecolor="white")
axes[1, 1].set_title("Объявлений по районам")
plt.sca(axes[1, 1]); plt.xticks(rotation=20, ha="right")

# 6. Матрица корреляций
num_cols = ["площадь_м2", "комнат", "этаж", "год_постройки",
            "удаленность_от_центра_км", "цена_за_м2"]
corr = df[num_cols].corr()
im = axes[1, 2].imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
labels = ["площадь", "комнат", "этаж", "год", "до_центра", "цена/м²"]
axes[1, 2].set_xticks(range(len(labels))); axes[1, 2].set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
axes[1, 2].set_yticks(range(len(labels))); axes[1, 2].set_yticklabels(labels, fontsize=8)
for i in range(len(labels)):
    for j in range(len(labels)):
        axes[1, 2].text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center",
                        fontsize=7, color="white" if abs(corr.iloc[i,j]) > 0.5 else "black")
axes[1, 2].set_title("Матрица корреляций")
plt.colorbar(im, ax=axes[1, 2])

plt.tight_layout()
plt.savefig("eda_ryazan.png", dpi=150, bbox_inches="tight")
print("✅ Графики сохранены: eda_ryazan.png")