import assert from 'node:assert/strict';
import test from 'node:test';
import { baguetteWidthPixels, previewGeometry } from './previewGeometry.js';

test('baguette width in metres uses the same scale as mat dimensions in centimetres', () => {
  assert.equal(baguetteWidthPixels('0.06'), 30);
  assert.equal(baguetteWidthPixels('0.05'), 25);
  assert.equal(baguetteWidthPixels(0.1), 50);
  assert.equal(baguetteWidthPixels(0.001), 1);
  assert.equal(baguetteWidthPixels(null), 50);
  assert.equal(baguetteWidthPixels('invalid'), 50);
});

test('mat position follows window size regardless of selection order', () => {
  for (const ids of [[1, 2], [2, 1]]) {
    const result = previewGeometry({ x1: 40, x2: 40, passepartouts: ids.map((id) => ({
      passepartout_id: id, window_length: id === 1 ? 30 : 20, window_width: id === 1 ? 30 : 20,
    })) });
    assert.deepEqual(result.mats.map((m) => m.passepartout_id), [1, 2]);
    assert.equal((result.height - result.mats[0].windowHeight) / 2, 5);
    assert.equal((result.mats[0].windowHeight - result.mats[1].windowHeight) / 2, 5);
  }
});

test('rectangular mats preserve separate horizontal and vertical margins', () => {
  const { height, width, mats } = previewGeometry({ frames: [{x1: 40, x2: 50}], passepartouts: [{
    passepartout_id: 1, passepartout_length: 40, passepartout_width: 50,
    window_length: 30, window_width: 20,
  }] });
  assert.equal((height - mats[0].windowHeight) / 2, 5);
  assert.equal((width - mats[0].windowWidth) / 2, 15);
});
