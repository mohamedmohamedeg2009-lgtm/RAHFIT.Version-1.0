import { Component, type ErrorInfo, type ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

/** Prevents an uncaught render error from taking down the entire browser document. */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = { hasError: false };

  public static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Replace with an observability adapter when a provider is selected.
    console.error("Unhandled UI error", error, errorInfo);
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return <main role="alert">An unexpected error occurred.</main>;
    }
    return this.props.children;
  }
}
