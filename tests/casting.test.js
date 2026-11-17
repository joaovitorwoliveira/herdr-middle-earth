// Run with: node --test tests/casting.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { pickHero } from "../mods/fellowship/casting.js";

const CAST = ["gandalf", "aragorn", "frodo", "sam", "legolas", "gimli"];

test("first free character", () => {
  assert.equal(pickHero(CAST, []), "gandalf");
  assert.equal(pickHero(CAST, ["gandalf", "frodo"]), "aragorn");
});

test("starts over when everyone is cast", () => {
  assert.equal(pickHero(CAST, CAST), "gandalf");
  assert.equal(pickHero(CAST, [...CAST, "gandalf"]), "aragorn");
  assert.equal(pickHero(CAST, [...CAST, "gandalf", "aragorn"]), "frodo");
});

test("fills a gap left by a closed agent before repeating", () => {
  assert.equal(pickHero(CAST, [...CAST, "gandalf", "aragorn"].filter((h) => h !== "sam")), "sam");
});
