interface BrandLogoProps {
  className?: string;
}

/** The only visual brand mark: the RAHFIT wordmark. */
export function BrandLogo({ className = "" }: BrandLogoProps) {
  return (
    <span className={`brand-logo ${className}`} aria-label="RAHFIT">
      RAH<span>FIT</span>
    </span>
  );
}
