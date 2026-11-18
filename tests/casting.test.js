// Run with: node --test tests/casting.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { pickHero, rollRare } from "../mods/fellowship/casting.js";

const CAST = ["gandalf", "aragorn", "frodo", "sam", "legolas", "gimli"];
const FIRST = () => 0;
const LAST = () => 0.999;

test("picks at random among the free characters", () => {
  assert.equal(pickHero(CAST, [], FIRST), "gandalf");
  assert.equal(pickHero(CAST, [], LAST), "gimli");
  assert.equal(pickHero(CAST, ["gandalf", "frodo"], FIRST), "aragorn");
  assert.equal(pickHero(CAST, ["gandalf", "frodo"], LAST), "gimli");
});

test("never repeats while someone is free", () => {
  for (let i = 0; i < 200; i++) {
    const hero = pickHero(CAST, ["gandalf", "aragorn", "frodo", "sam", "legolas"]);
    assert.equal(hero, "gimli");
  }
});

test("starts over when everyone is cast", () => {
  assert.equal(pickHero(CAST, CAST, FIRST), "gandalf");
  assert.equal(pickHero(CAST, CAST, LAST), "gimli");
  assert.equal(pickHero(CAST, [...CAST, "gandalf"], FIRST), "aragorn");
});

test("fills a gap left by a closed agent before repeating", () => {
  assert.equal(pickHero(CAST, [...CAST, "gandalf", "aragorn"].filter((h) => h !== "sam"), LAST), "sam");
});

test("a rare edition comes up 3% of the time", () => {
  assert.equal(rollRare(() => 0), true);
  assert.equal(rollRare(() => 0.029), true);
  assert.equal(rollRare(() => 0.03), false);
  assert.equal(rollRare(() => 0.5), false);
});
