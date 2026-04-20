import * as React from "react";
import { cn } from "@/lib/utils";

// Lightweight label — shadcn usually wraps @radix-ui/react-label, but a
// plain <label> is enough for our forms and avoids another dependency.
const Label = React.forwardRef(({ className, ...props }, ref) => (
  <label
    ref={ref}
    className={cn(
      "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
      className,
    )}
    {...props}
  />
));
Label.displayName = "Label";

export { Label };
