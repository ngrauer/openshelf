import { BookOpen, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const CONDITION_LABELS = {
  new: "New",
  like_new: "Like New",
  good: "Good",
  fair: "Fair",
  poor: "Poor",
};

const CONDITION_COLORS = {
  new: "bg-emerald-100 text-emerald-800",
  like_new: "bg-emerald-50 text-emerald-700",
  good: "bg-blue-50 text-blue-700",
  fair: "bg-amber-50 text-amber-800",
  poor: "bg-rose-50 text-rose-700",
};

function formatPrice(value) {
  if (value == null) return "—";
  return `$${Number(value).toFixed(2)}`;
}

export function ListingCard({ listing, matchScore, onContactSeller }) {
  const navigate = useNavigate();
  if (!listing) return null;
  const tb = listing.textbook;
  const seller = listing.seller;
  const conditionKey = listing.condition;
  const coverUrl = listing.image_url || tb?.image_url;

  return (
    <Card
      className="flex h-full cursor-pointer flex-col transition-shadow hover:shadow-md"
      onClick={() => navigate(`/listings/${listing.id}`)}
    >
      {/* Book cover image */}
      <div className="relative flex h-40 items-center justify-center overflow-hidden rounded-t-lg bg-muted">
        {coverUrl ? (
          <img
            src={coverUrl}
            alt={tb?.title ?? "Textbook cover"}
            className="h-full w-full object-cover"
            onError={(e) => { e.target.style.display = "none"; e.target.nextSibling.style.display = "flex"; }}
          />
        ) : null}
        <div
          className={cn("flex h-full w-full items-center justify-center", coverUrl && "hidden")}
        >
          <BookOpen className="h-12 w-12 text-muted-foreground/40" />
        </div>
        {matchScore != null && (
          <span className="absolute right-2 top-2 inline-flex items-center gap-1 rounded-full bg-primary/90 px-2 py-0.5 text-xs font-medium text-primary-foreground">
            <Sparkles className="h-3 w-3" />
            {Math.round(matchScore)}%
          </span>
        )}
      </div>
      <CardHeader className="space-y-2 pt-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="line-clamp-2 text-base">
            {tb?.title ?? "Untitled textbook"}
          </CardTitle>
        </div>
        <p className="line-clamp-1 text-xs text-muted-foreground">
          {tb?.author}
          {tb?.edition ? ` · ${tb.edition}` : ""}
        </p>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <div className="text-2xl font-bold">{formatPrice(listing.price)}</div>
          {tb?.retail_price && (
            <div className="text-xs text-muted-foreground line-through">
              {formatPrice(tb.retail_price)}
            </div>
          )}
        </div>

        <span
          className={cn(
            "inline-flex w-fit rounded-full px-2 py-0.5 text-xs font-medium",
            CONDITION_COLORS[conditionKey] ?? "bg-muted text-foreground",
          )}
        >
          {CONDITION_LABELS[conditionKey] ?? conditionKey}
        </span>

        {listing.description && (
          <p className="line-clamp-2 text-xs text-muted-foreground">
            {listing.description}
          </p>
        )}

        <div className="mt-auto flex items-center justify-between pt-2">
          <div className="text-xs text-muted-foreground">
            {seller ? `${seller.first_name} ${seller.last_name}` : "Unknown seller"}
          </div>
          {onContactSeller && (
            <Button
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onContactSeller(listing);
              }}
            >
              Contact
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
