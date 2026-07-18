import "@testing-library/jest-dom/vitest";

const motionTestStyles = document.createElement("style");
motionTestStyles.textContent =
  ".dashboard-page [style*='opacity: 0'], .dashboard-page [style*='opacity:0'] { opacity: 1 !important; transform: none !important; }";
document.head.append(motionTestStyles);

class MockIntersectionObserver implements IntersectionObserver {
  readonly root: Element | Document | null;
  readonly rootMargin: string;
  readonly thresholds: ReadonlyArray<number>;
  private readonly callback: IntersectionObserverCallback;

  constructor(callback: IntersectionObserverCallback, options?: IntersectionObserverInit) {
    this.callback = callback;
    this.root = options?.root ?? null;
    this.rootMargin = options?.rootMargin ?? "0px";
    this.thresholds = Array.isArray(options?.threshold)
      ? options.threshold
      : [options?.threshold ?? 0];
  }

  observe(target: Element): void {
    const boundingClientRect = target.getBoundingClientRect();

    this.callback(
      [
        {
          boundingClientRect,
          intersectionRatio: 1,
          intersectionRect: boundingClientRect,
          isIntersecting: true,
          rootBounds: null,
          target,
          time: 0,
        },
      ],
      this,
    );
  }

  unobserve(target: Element): void {
    void target;
  }

  disconnect(): void {}

  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
}

Object.defineProperty(window, "IntersectionObserver", {
  configurable: true,
  value: MockIntersectionObserver,
  writable: true,
});

Object.defineProperty(globalThis, "IntersectionObserver", {
  configurable: true,
  value: MockIntersectionObserver,
  writable: true,
});
