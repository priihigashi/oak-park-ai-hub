#!/usr/bin/env python3
"""Build Food App v2 from the current live personal site plus 16 vetted captures."""
from __future__ import annotations

import re
from pathlib import Path

import requests
from PIL import Image, ImageOps

LIVE = "https://priscila-mike-recipes.priih.chatgpt.site"
OUT = Path("docs/food-app")
ASSETS = [
    "framework-DjPHiq1u.js",
    "index-CzN0bzCZ.js",
    "index-Dv1be0a-.css",
    "layout-segment-context-Cef6g9lU.js",
    "page-DwBm2Rih.js",
    "rolldown-runtime-S-ySWqyJ.js",
]

NEW_CALLS = r'''a(`no-dough-chicken-coxinha`,`No-Dough Chicken Coxinha`,null,null,`Chicken`,`1 kg chicken fillet (cut in half for easier cooking)|200 ml tomato sauce|salt (to taste)|black pepper (to taste)|paprika (to taste)|parsley (to taste)|300 grams requeijão or cream cheese (as filling)|1 clove garlic (diced)|eggs (for breading)|milk (for breading, as needed)|all-purpose flour (for breading, as needed)|oil (for frying)`,[`Cut the chicken fillets in half and cook them; use a pressure cooker for faster results.`,`Shred the cooked chicken using a fork or shake in the pressure cooker.`,`Sauté garlic in a pan, add tomato sauce, and season with salt, black pepper, and paprika.`,`Add shredded chicken to the pan and let it cook on low heat, stirring to avoid burning.`,`Once the chicken is dry, let it cool, and mix with parsley and requeijão or cream cheese.`,`Form the mixture into small coxinha shapes.`,`Prepare breading by using eggs, milk, and flour. Dip the coxinhas in this mixture, then in flour.`,`Fry the coxinhas at 180°C (356°F) until golden brown.`,`Serve them warm, optionally with grated parmesan and seasoned mayonnaise.`]),a(`bread-scrap-pizza`,`Bread-Scrap Pizza`,15,null,`Meat`,`4 old bread pieces (torn into chunks)|300 ml water|olive oil (a drizzle)|1 package grated Parmesan cheese|oregano (a pinch)|tomato sauce|mozzarella cheese (preferably Swift brand)|finely sliced calabrese sausage (Swift brand, as a novelty)|onion (optional)|ketchup (optional)`,[`Tear the old bread into chunks and mix with water in a bowl.`,`Add a drizzle of olive oil and knead the mixture until it forms a homogeneous dough.`,`Mix in the grated Parmesan cheese and a pinch of oregano.`,`Spread the dough onto a greased baking sheet, forming a thin layer.`,`Drizzle with a bit more olive oil.`,`Preheat the oven to 230 degrees Celsius and bake for 10 minutes or until the edges are crisp.`,`Spread tomato sauce over the baked base.`,`Top with mozzarella cheese and finely sliced calabrese sausage.`,`Add onions and sprinkle more oregano if desired.`,`Return to the oven until the cheese is fully melted.`,`Serve and optionally accompany with ketchup.`]),a(`easy-chicken-esfiha-style-foldover`,`Easy Chicken Esfiha-Style Foldover`,10,1,`Chicken`,`1 Rap10/Rapidez-style flatbread (or a medium whole-wheat tortilla)|shredded chicken (enough for one foldover)|1 slice mozzarella cheese|light requeijão (thin layer around the edge to seal; light cream cheese works too)|1 egg yolk (beaten, for brushing)|sesame seeds (optional)`,[`Lay the flatbread on a work surface and place shredded chicken in the center.`,`Top with 1 slice of mozzarella.`,`Spread a thin line of light requeijão around the edge to help seal the foldover.`,`Fold into the esfiha-style shape and pinch the edges closed.`,`Brush with beaten egg yolk and add sesame seeds if using.`,`Air-fry at 200°C (390°F) for 10 minutes, or until the outside is golden and the filling is hot.`]),a(`banana-neapolitan-nice-cream`,`Banana Neapolitan Nice Cream`,null,null,`Vegetarian`,`3 banana (peeled, for the white part)|honey (to taste, for sweetening the white part)|3 banana (peeled, for the strawberry part)|strawberry (frozen, for the strawberry part)|honey (to taste, for sweetening the strawberry part)|3 banana (peeled, for the chocolate part)|2 tablespoons cocoa powder (for the chocolate part)|honey (to taste, for sweetening the chocolate part)`,[`Peel and freeze the bananas and strawberries by placing them in bags in the freezer until solid.`,`For the white part, blend 3 bananas with a little honey until smooth and creamy.`,`For the strawberry part, blend 3 bananas with frozen strawberries and a touch of honey until smooth.`,`For the chocolate part, blend 3 bananas with 2 tablespoons of cocoa powder and some honey until smooth.`,`Layer the mixtures in a container to create the classic Neapolitan look, then freeze until set.`]),a(`crispy-air-fryer-chicken-with-lemon-garlic-sauce`,`Crispy Air-Fryer Chicken with Lemon-Garlic Sauce`,42,null,`Chicken`,`500 grams chicken breast (cut into strips)|2 eggs (preferably free-range)|1 tablespoon mustard|1 tablespoon paprika|1 lemon (juiced)|salt (to taste)|2 tablespoons chopped parsley|200 grams corn flour|30 grams grated parmesan cheese|3 tablespoons light cream cheese (for the sauce)|1/2 lemon (juiced for the sauce)|2 cloves garlic (grated, for the sauce)|30 ml skimmed milk (for the sauce)|pepper (to taste for the sauce)`,[`Cut 500 grams of chicken breast into strips.`,`In a bowl, beat 2 eggs with 1 tablespoon of mustard, 1 tablespoon of paprika, the juice of one lemon, salt to taste, and 2 tablespoons of chopped parsley.`,`Marinate the chicken in the mixture for 30 minutes.`,`Blend 200 grams of corn flour with 30 grams of grated parmesan cheese.`,`Coat the marinated chicken in the flour mixture, then dip in the egg mixture again and coat with flour again.`,`Air-fry at 180°C (356°F) for 12 minutes, turning once if needed for even browning.`,`For the sauce, mix 3 tablespoons of light cream cheese, the juice of half a lemon, 2 grated cloves of garlic, 30 ml of skimmed milk, and adjust salt and pepper to taste.`]),a(`lighter-cheddar-mcmelt-style-burger`,`Lighter Cheddar McMelt-Style Burger`,10,1,`Meat`,`90 g ground beef top round (molded into a burger, use chicken for variation)|salt (to taste)|pepper (to taste)|1 tbsp light cheddar cream cheese|2 tbsp light ricotta cream|0.5 onion (sliced for caramelizing)|1 tsp light soy sauce|Australian bread (for the burger bun)`,[`Mold 90g of ground top round beef into a burger patty and season with salt and pepper.`,`Air-fry the patty at 200°C (390°F) for about 10 minutes, or cook until it reaches a safe doneness and your preferred texture.`,`In a small bowl, microwave 1 tbsp of light cheddar cream cheese and 2 tbsp of light ricotta cream for 10 seconds until melted.`,`Slice half an onion and caramelize it in a pan over low heat. Add 1 tsp of light soy sauce and gradually add water until fully caramelized.`,`Assemble the burger with Australian bread, the beef patty, the cheese cream, caramelized onions, and top with the other half of the bun.`]),a(`ginger-soy-chicken-marinade`,`Ginger-Soy Chicken Marinade`,null,null,`Chicken`,`chicken cubes (amount as needed for this marinade)|10 grams ginger|20 ml apple cider vinegar|5 grams black pepper|10 grams green onions|30 ml light soy sauce|3 cloves garlic|salt (to taste)|50 ml water (to mix)`,[`Mix the ginger, apple cider vinegar, black pepper, green onions, soy sauce, garlic, and salt with water.`,`Place chicken cubes in a ziploc bag and pour the marinade over them.`,`Let marinate for at least two hours.`,`Cook on skewers in the air fryer.`]),a(`zucchini-pancakes-with-beef-vegetable-filling`,`Zucchini Pancakes with Beef & Vegetable Filling`,null,null,`Meat`,`zucchini (use 100 g peeled zucchini for the pancake batter; remaining zucchini goes into the filling)|1 carrot (chopped)|1 egg|35 grams flour|garlic (to taste)|salt (to taste)|tomato passata|ground beef`,[`Peel the zucchini and set aside half of it.`,`Saute the half zucchini with chopped carrot and a bit of garlic.`,`Season with salt and cook until golden.`,`Add tomato passata and cook on medium heat.`,`Blend 100 grams of the peeled zucchini with an egg, 35 grams of flour, and a bit of salt until smooth.`,`Pour a thin layer into a non-stick pan to make pancakes.`,`Blend the sautéed carrot and zucchini into a sauce and mix with ground beef for the filling.`,`Assemble the pancakes with the filling.`]),a(`airy-milk-powder-protein-dessert`,`Airy Milk-Powder Protein Dessert`,120,null,`Vegetarian`,`4 pasteurized egg whites (beat to stiff peaks; use pasteurized egg whites because the dessert is not cooked)|20 grams skim milk powder (dissolved in liquid)|20 ml skim milk (liquid)|20 grams condensed milk`,[`Beat 4 pasteurized egg whites until stiff peaks form.`,`Mix 20 grams of skim milk powder with 20 ml of skim milk to make a creamy mixture.`,`Gently fold the milk mixture into the beaten egg whites until homogeneous.`,`Finish by adding 20 grams of condensed milk, mixing gently.`,`Refrigerate for 5 hours for a pudding-like texture or freeze for 2 hours for an ice-cream-like texture.`]),a(`moist-chocolate-oat-cake-with-cocoa-syrup`,`Moist Chocolate Oat Cake with Cocoa Syrup`,25,1,`Vegetarian`,`1 egg|2 tbsp oat flour|1 tbsp cocoa powder (100%)|1 tbsp culinary sweetener (your choice)|1 tbsp milk (or substitute with water)|1 tsp baking powder|1 cup milk (for syrup)|1 tbsp cocoa powder (for syrup)|2 tbsp culinary sweetener (for syrup)|1 tsp corn starch (for syrup)`,[`Preheat the oven or air fryer to 180°C (356°F).`,`In a mixing bowl, whisk the egg, oat flour, cocoa powder, and sweetener.`,`Add the milk (or water) and mix well.`,`Stir in the baking powder until combined.`,`Pour the mixture into a baking dish and bake for 25 minutes or until set.`,`For the syrup: In a saucepan, mix the milk, cocoa powder, sweetener, and corn starch.`,`Heat on low, stirring constantly, until thickened to the desired consistency.`,`Poke holes in the cake with a skewer and pour the syrup over.`,`Let it soak and absorb the syrup before serving.`]),a(`one-pot-chuck-roast-with-vegetables`,`One-Pot Chuck Roast with Vegetables`,60,null,`Meat`,`1 celery stalk (chopped)|2 carrots (chopped)|1 onion (chopped)|mushrooms (cooked for 5 minutes)|1 chuck roast (cut into two large chunks)|black pepper (to taste)|kosher salt (to taste)|olive oil (for searing)|garlic (to taste)|tomato paste (to taste)|low sodium beef broth (to taste)|1 teaspoon fresh rosemary (or dried)|dried thyme (if fresh thyme unavailable)`,[`Chop the celery, carrots, and onions.`,`Sear the chunks of beef in olive oil, seasoned with salt and black pepper.`,`In the same pot, cook the mushrooms for 5 minutes until they appear slightly crispy.`,`Add the celery, carrots, and onions to the pot and cook for 5 more minutes.`,`Add garlic, tomato paste, and beef broth to the pot.`,`Add rosemary and thyme (if using dried), and return the beef to the pot.`,`Season with salt and black pepper, bring to a boil, then reduce heat and simmer for one hour.`]),a(`caramelized-onion-sun-dried-tomato-pasta`,`Caramelized Onion & Sun-Dried Tomato Pasta`,60,null,`Vegetarian`,`onions (thinly sliced; source does not specify amount)|pasta (enough for the amount of sauce; source does not specify shape or quantity)|sun-dried tomatoes|paprika|Italian seasoning|dried parsley|dash salt|black pepper|a lot garlic|olive oil|coconut milk|juice from 1 lemon|fresh parsley|freshly grated Parmesan cheese`,[`Preheat oven to 400°F.`,`Thinly slice onions using a mandolin.`,`Add sun-dried tomatoes, paprika, Italian seasoning, dried parsley, salt, and black pepper to the onions.`,`Add a lot of garlic and drizzle with olive oil.`,`Mix everything well, cover with tinfoil, and bake for an hour.`,`With 10 minutes left, boil the pasta.`,`Reserve some pasta water and drain the rest.`,`Add coconut milk and lemon juice to the pasta.`,`Mix in cooked pasta and pasta water along with fresh parsley.`,`Top with freshly grated Parmesan cheese.`]),a(`strawberry-protein-mousse`,`Strawberry Protein Mousse`,null,5,`Vegetarian`,`1 packet zero-sugar strawberry gelatin (use a vegetarian gelatin alternative if needed)|1 cup non-fat natural yogurt|100 grams frozen strawberries|1 scoop whey protein (Your favorite flavor)`,[`In a blender, combine the zero-sugar gelatin, non-fat natural yogurt, frozen strawberries, and whey protein.`,`Blend until smooth and creamy.`,`Divide the mixture into individual serving cups or pour it into a large container.`,`Chill in the refrigerator until set, and serve cold.`]),a(`street-corn-sweet-potato-beef-bowls`,`Street-Corn Sweet Potato & Beef Bowls`,45,4,`Meat`,`4 large sweet potatoes|oil (for coating)|salt (to taste)|pepper (to taste)|2 cups corn|150 grams Greek yogurt|60 grams light mayo|60 grams Cotija cheese|red onion (chopped)|jalapeno (chopped)|2 limes (juiced)|cilantro (chopped)|1 teaspoon chili powder|1 tablespoon Tajin (to taste)|1.5 pounds ground beef|cumin (to taste)|garlic powder (to taste)|chili powder (to taste)`,[`Wash and cut four large sweet potatoes in half, cutting on the flat side.`,`Coat each sweet potato half with oil, sprinkle with salt and pepper.`,`Place sweet potatoes oil-side down on a baking tray and cook at 425°F for about 45 minutes.`,`In a mixing bowl, combine corn, Greek yogurt, light mayo, Cotija cheese, chopped red onion, jalapeno, lime juice, cilantro, chili powder, Tajin, salt, and pepper. Mix well.`,`Cook ground beef in a pan with cumin, garlic powder, chili powder, salt, and pepper until seared on one side, then chop and cook until fully cooked and browned.`,`Mash the cooked sweet potatoes slightly, then top with ground beef and street corn mix.`]),a(`creamy-beef-cassava-vegetable-soup`,`Creamy Beef, Cassava & Vegetable Soup`,18,null,`Meat`,`500 g sirloin steak (cut into small pieces)|2 cloves garlic (minced)|1 tsp salt|1 tsp paprika|2 potatoes (peeled and cubed)|2 cups cassava (peeled and cubed)|1 carrot (peeled and cubed)|4 cups water|200 g pasta (small type like ditalini or elbow)`,[`In a pressure cooker, sauté the sirloin steak pieces with minced garlic until browned.`,`Add salt and paprika to the meat.`,`Add potatoes, cassava, and carrot to the pan.`,`Pour water to cover the ingredients. Seal the pressure cooker and cook for 15 minutes.`,`Release the pressure and remove only the vegetables from the pot.`,`Place the pasta in the pressure cooker and cook under pressure for 3 minutes.`,`Blend the removed vegetables with some of the cooking liquid to make a cream.`,`Stir the vegetable cream back into the pressure cooker with the pasta and beef. Adjust the seasoning with salt if needed.`]),a(`cheddar-onion-beef-flatbread`,`Cheddar-Onion Beef Flatbread`,null,1,`Meat`,`1 Rap10/Rapdess-style flatbread (or a medium tortilla)|110 g lean ground beef (creator says this yields about 75 g cooked)|25 g cheddar cheese (use 25 g as the creator's calculated version)|30 ml skim milk (for melting with cheddar)|onion (to taste, caramelized without added sugar)`,[`Place the flatbread on a plate or work surface.`,`Season 110 g lean ground beef with salt and sear it in a very hot nonstick skillet without added oil, breaking or shaping it as desired, until safely cooked.`,`Microwave 25 g cheddar with 30 ml skim milk until melted and smooth; heat in short intervals and stir to prevent scorching.`,`Cook sliced onion in a skillet without sugar, adding small splashes of water as needed, until deeply softened and browned.`,`Top the flatbread with the cooked beef, cheddar sauce and caramelized onion. Fold or serve open-faced.`])'''

SLUGS = [
    "no-dough-chicken-coxinha", "bread-scrap-pizza", "easy-chicken-esfiha-style-foldover",
    "banana-neapolitan-nice-cream", "crispy-air-fryer-chicken-with-lemon-garlic-sauce",
    "lighter-cheddar-mcmelt-style-burger", "ginger-soy-chicken-marinade",
    "zucchini-pancakes-with-beef-vegetable-filling", "airy-milk-powder-protein-dessert",
    "moist-chocolate-oat-cake-with-cocoa-syrup", "one-pot-chuck-roast-with-vegetables",
    "caramelized-onion-sun-dried-tomato-pasta", "strawberry-protein-mousse",
    "street-corn-sweet-potato-beef-bowls", "creamy-beef-cassava-vegetable-soup",
    "cheddar-onion-beef-flatbread",
]

CHOICES = {
    "no-dough-chicken-coxinha": ("candidate", "no-dough-chicken-coxinha__2.jpg", (.18,.42,.92,.70)),
    "bread-scrap-pizza": ("candidate", "bread-scrap-pizza__0.jpg", (0,0,1,.55)),
    "easy-chicken-esfiha-style-foldover": ("candidate", "easy-chicken-esfiha-style-foldover__0.jpg", (.05,.20,.95,.68)),
    "banana-neapolitan-nice-cream": ("candidate", "banana-neapolitan-nice-cream__2.jpg", (0,.42,1,.90)),
    "crispy-air-fryer-chicken-with-lemon-garlic-sauce": ("candidate", "crispy-air-fryer-chicken-with-lemon-garlic-sauce__0.jpg", (0,.28,1,.82)),
    "lighter-cheddar-mcmelt-style-burger": ("candidate", "lighter-cheddar-mcmelt-style-burger__0.jpg", (0,0,1,.58)),
    "ginger-soy-chicken-marinade": ("candidate", "ginger-soy-chicken-marinade__2.jpg", (0,.40,1,.95)),
    "zucchini-pancakes-with-beef-vegetable-filling": ("cover", "zucchini-pancakes-with-beef-vegetable-filling.jpg", (.20,.28,.80,.78)),
    "airy-milk-powder-protein-dessert": ("candidate", "airy-milk-powder-protein-dessert__2.jpg", (0,.50,1,.98)),
    "moist-chocolate-oat-cake-with-cocoa-syrup": ("candidate", "moist-chocolate-oat-cake-with-cocoa-syrup__0.jpg", (0,.35,1,.92)),
    "one-pot-chuck-roast-with-vegetables": ("candidate", "one-pot-chuck-roast-with-vegetables__2.jpg", (0,.45,1,.98)),
    "caramelized-onion-sun-dried-tomato-pasta": ("candidate", "caramelized-onion-sun-dried-tomato-pasta__2.jpg", (0,.40,1,.96)),
    "strawberry-protein-mousse": ("candidate", "strawberry-protein-mousse__1.jpg", (0,.55,1,1)),
    "street-corn-sweet-potato-beef-bowls": ("candidate", "street-corn-sweet-potato-beef-bowls__1.jpg", (0,.28,1,.82)),
    "creamy-beef-cassava-vegetable-soup": ("candidate", "creamy-beef-cassava-vegetable-soup__0.jpg", (0,.36,1,.92)),
    "cheddar-onion-beef-flatbread": ("candidate", "cheddar-onion-beef-flatbread__1.jpg", (0,.48,1,1)),
}

CARD_OLD = "(0,f.jsxs)(`span`,{children:[e.time,` min`]}),(0,f.jsxs)(`span`,{children:[`Serves `,e.serves]})"
CARD_NEW = "(0,f.jsx)(`span`,{children:e.time!=null?`${e.time} min`:`Time varies`}),(0,f.jsx)(`span`,{children:e.serves!=null?`Serves ${e.serves}`:`Serves flexible`})"
MODAL_OLD = "(0,f.jsxs)(`span`,{children:[a.time,` minutes`]}),(0,f.jsxs)(`span`,{children:[`Serves `,a.serves]})"
MODAL_NEW = "(0,f.jsx)(`span`,{children:a.time!=null?`${a.time} minutes`:`Time varies`}),(0,f.jsx)(`span`,{children:a.serves!=null?`Serves ${a.serves}`:`Serves flexible`})"


def get(url: str) -> bytes:
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    return response.content


def patch_html(text: str) -> str:
    text = text.replace('"/assets/', '"./assets/').replace('"/favicon.svg', '"./favicon.svg')
    text = re.sub(r'<script>\(function\(\)\{function c\(\).*?challenge-platform/scripts/jsd/main\.js.*?</script>', '', text, flags=re.S)
    return text


def patch_page(text: str) -> str:
    if "no-dough-chicken-coxinha" in text:
        raise RuntimeError("Live source already contains v2 recipes; refusing to append duplicates")
    text = text.replace('],s={', ',' + NEW_CALLS + '],s={', 1)
    entries = ','.join(f'"{slug}":`./images/{slug}.webp`' for slug in SLUGS)
    text = text.replace('},d=[', ',' + entries + '},d=[', 1)
    text = text.replace(CARD_OLD, CARD_NEW).replace(MODAL_OLD, MODAL_NEW)
    if text.count('a(`') != 65:
        raise RuntimeError(f"Expected exactly 65 recipes after patch; got {text.count('a(`')}")
    if text.count('./images/') != 16:
        raise RuntimeError("Expected exactly 16 local image references")
    return text


def crop_image(source: Path, box: tuple[float,float,float,float], dest: Path) -> None:
    image = Image.open(source).convert("RGB")
    width, height = image.size
    left, top, right, bottom = box
    region = image.crop((int(left*width), int(top*height), int(right*width), int(bottom*height)))
    final = ImageOps.fit(region, (800, 533), method=Image.Resampling.LANCZOS)
    final.save(dest, "WEBP", quality=78, method=6)


def build_images(candidate_dir: Path, cover_dir: Path) -> None:
    image_dir = OUT / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    for slug, (kind, filename, box) in CHOICES.items():
        base = candidate_dir if kind == "candidate" else cover_dir
        source = base / filename
        if not source.exists():
            raise FileNotFoundError(source)
        crop_image(source, box, image_dir / f"{slug}.webp")


def main() -> int:
    candidate_dir = Path("/tmp/food-app-frame-candidates")
    cover_dir = Path("/tmp/food-app-source-images")
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    index = patch_html(get(LIVE + "/").decode("utf-8", errors="ignore"))
    (OUT / "index.html").write_text(index, encoding="utf-8")
    (OUT / "favicon.svg").write_bytes(get(LIVE + "/favicon.svg"))
    for asset in ASSETS:
        data = get(f"{LIVE}/assets/{asset}")
        if asset == "page-DwBm2Rih.js":
            data = patch_page(data.decode("utf-8")).encode("utf-8")
        (OUT / "assets" / asset).write_bytes(data)
    build_images(candidate_dir, cover_dir)
    (OUT / "BUILD.txt").write_text(
        "Food App v2\n49 existing recipes preserved\n16 vetted recipes added\n12 incomplete captures intentionally held\n",
        encoding="utf-8",
    )
    print("Food App Pages build complete: 65 recipes, 16 new images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
