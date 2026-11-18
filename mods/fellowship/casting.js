// A random pick among the least-cast characters: every character gets a turn before anyone repeats.
export function pickHero(pool, heroes, random = Math.random) {
  const uses = (hero) => heroes.filter((h) => h === hero).length;
  const fewest = Math.min(...pool.map(uses));
  const choices = pool.filter((hero) => uses(hero) === fewest);
  return choices[Math.floor(random() * choices.length)];
}

export const RARE_CHANCE = 0.03;

export const rollRare = (random = Math.random) => random() < RARE_CHANCE;
