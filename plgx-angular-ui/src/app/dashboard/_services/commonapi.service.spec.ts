import { TestBed } from '@angular/core/testing';

import { CommonapiService } from './commonapi.service';

describe('CommonapiService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: CommonapiService = TestBed.get(CommonapiService);
    expect(service).toBeTruthy();
  });
});
