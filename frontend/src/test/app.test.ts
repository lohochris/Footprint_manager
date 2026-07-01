import { describe, it, expect } from 'vitest';

import { APP_NAME, APP_VERSION } from '@/utils/constants';

describe('constants', () => {
  it('defines application name', () => {
    expect(APP_NAME).toBe('Footprint Manager');
  });

  it('defines application version', () => {
    expect(APP_VERSION).toBe('0.1.0');
  });
});
