// The least-cast character, first in pool order on a tie: free ones go first, then the cast starts over.
export function pickHero(pool, heroes) {
  const uses = (hero) => heroes.filter((h) => h === hero).length;
  return pool.reduce((best, hero) => (uses(hero) < uses(best) ? hero : best));
}
