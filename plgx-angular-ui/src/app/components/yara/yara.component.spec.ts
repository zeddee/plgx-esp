import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { YaraComponent } from './yara.component';

describe('YaraComponent', () => {
  let component: YaraComponent;
  let fixture: ComponentFixture<YaraComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ YaraComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(YaraComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
