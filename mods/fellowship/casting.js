// A random pick among the least-cast characters: every character gets a turn before anyone repeats.
export function pickHero(pool, heroes, random = Math.random) {
  const uses = (hero) => heroes.filter((h) => h === hero).length;
  const fewest = Math.min(...pool.map(uses));
  const choices = pool.filter((hero) => uses(hero) === fewest);
  return choices[Math.floor(random() * choices.length)];
}

export const RARE_CHANCE = 0.03;
export const SAX_CHANCE = 0.01;
const SAX_HERO = "gandalf";

// The edition a fresh casting draws: "sax" (Gandalf only, tried first), "rare", or null.
export function drawEdition(hero, random = Math.random) {
  if (hero === SAX_HERO && random() < SAX_CHANCE) return "sax";
  return random() < RARE_CHANCE ? "rare" : null;
}
