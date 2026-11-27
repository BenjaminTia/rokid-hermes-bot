import test from 'node:test';
import assert from 'node:assert/strict';
import { splitVisual } from '../lib/visual.js';
test('plain text unchanged', () => assert.deepEqual(splitVisual('Hello'), {text:'Hello',visual:null}));
test('formula is bounded and removed from spoken text', () => assert.deepEqual(splitVisual('Energy. <visual>{"type":"formula","tex":"E=mc^2"}</visual>'), {text:'Energy.',visual:{type:'formula',tex:'E=mc^2'}}));
test('chart values become series objects', () => assert.deepEqual(splitVisual('Trend <visual>{"type":"chart","points":[1,-2,3]}</visual>'), {text:'Trend',visual:{type:'chart',points:[{value:1},{value:-2},{value:3}],caption:''}}));
test('partial JSON never spoken', () => assert.deepEqual(splitVisual('Trend <visual>{"type":'), {text:'Trend',visual:null}));
test('invalid and excessive payloads are ignored', () => { for (const x of ['{}','{"type":"chart","points":[1]}','{"type":"chart","points":[1,"x"]}','x'.repeat(4097)]) assert.equal(splitVisual('x<visual>'+x+'</visual>').visual,null); });
