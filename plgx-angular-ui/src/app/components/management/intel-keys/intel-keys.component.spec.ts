import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IntelKeysComponent } from './intel-keys.component';

describe('IntelKeysComponent', () => {
  let component: IntelKeysComponent;
  let fixture: ComponentFixture<IntelKeysComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ IntelKeysComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IntelKeysComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
