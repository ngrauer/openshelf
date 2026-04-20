import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  BookOpen,
  CheckCircle2,
  Loader2,
  MessageSquare,
  Sparkles,
  Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { DashboardLayout, DASHBOARD_VIEWS } from "@/components/DashboardLayout";
import { useAuth } from "@/contexts/AuthContext";
import { conversationsApi, listingsApi, reviewsApi, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

const CONDITION_LABELS = {
  new: "New",
  like_new: "Like New",
  good: "Good",
  fair: "Fair",
  poor: "Poor",
};

function formatPrice(value) {
  if (value == null) return "—";
  return `$${Number(value).toFixed(2)}`;
}

export function ListingDetailPage() {
  const { id } = useParams();
  const listingId = Number(id);
  const { user } = useAuth();
  const navigate = useNavigate();

  const listingQuery = useQuery({
    queryKey: ["listing", listingId],
    queryFn: () => listingsApi.get(listingId),
    enabled: Number.isFinite(listingId),
  });

  // Contact Seller — starts or resumes a conversation. If the buyer leaves
  // the message blank, the backend generates an agentic first message from
  // a template (see messaging_service.build_agentic_first_message).
  const [composerOpen, setComposerOpen] = useState(false);
  const [initialMessage, setInitialMessage] = useState("");
  const [startedConversationId, setStartedConversationId] = useState(null);
  const [contactError, setContactError] = useState(null);

  const startConversation = useMutation({
    mutationFn: () =>
      conversationsApi.start(listingId, initialMessage.trim() || undefined),
    onSuccess: (conv) => {
      setStartedConversationId(conv.id);
      setContactError(null);
    },
    onError: (err) => {
      setContactError(
        err instanceof ApiError ? err.message : "Could not start conversation",
      );
    },
  });

  const listing = listingQuery.data;
  const tb = listing?.textbook;
  const seller = listing?.seller;
  const isOwnListing = listing && user && listing.seller_id === user.id;

  return (
    <DashboardLayout
      view={DASHBOARD_VIEWS.SHOPPING}
      onViewChange={(next) => navigate(`/?view=${next}`)}
      onOpenChat={() => {}}
    >
      <div className="mx-auto max-w-4xl space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(-1)}
          className="-ml-2"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        {listingQuery.isLoading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading listing...
          </div>
        )}

        {listingQuery.isError && (
          <Card>
            <CardContent className="py-10 text-center text-sm text-muted-foreground">
              {listingQuery.error instanceof ApiError
                ? listingQuery.error.message
                : "Could not load listing"}
              <div className="mt-4">
                <Button asChild variant="outline" size="sm">
                  <Link to="/">Back to shopping</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {listing && (
          <div className="grid gap-6 md:grid-cols-[1fr_320px]">
            <Card>
              {/* Book cover image */}
              {(() => {
                const coverUrl = listing.image_url || tb?.image_url;
                return coverUrl ? (
                  <div className="flex h-64 items-center justify-center overflow-hidden rounded-t-lg bg-muted">
                    <img
                      src={coverUrl}
                      alt={tb?.title ?? "Textbook"}
                      className="h-full w-full object-contain"
                    />
                  </div>
                ) : null;
              })()}
              <CardHeader>
                <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted-foreground">
                  <BookOpen className="h-3 w-3" />
                  Textbook
                </div>
                <CardTitle className="text-2xl">
                  {tb?.title ?? "Untitled textbook"}
                </CardTitle>
                <CardDescription>
                  {tb?.author}
                  {tb?.edition ? ` · ${tb.edition}` : ""}
                  {tb?.publisher ? ` · ${tb.publisher}` : ""}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <InfoRow label="ISBN" value={tb?.isbn ?? "—"} />
                  <InfoRow label="Condition" value={CONDITION_LABELS[listing.condition] ?? listing.condition} />
                  <InfoRow label="Retail" value={formatPrice(tb?.retail_price)} />
                  <InfoRow label="Status" value={listing.status} />
                </div>

                {listing.description && (
                  <div>
                    <div className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Description
                    </div>
                    <p className="text-sm">{listing.description}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardDescription>Asking price</CardDescription>
                  <CardTitle className="text-4xl">
                    {formatPrice(listing.price)}
                  </CardTitle>
                  {listing.ai_recommended_price != null && (
                    <div className="flex items-center gap-1 pt-1 text-xs text-muted-foreground">
                      <Sparkles className="h-3 w-3 text-primary" />
                      AI suggested {formatPrice(listing.ai_recommended_price)}
                    </div>
                  )}
                </CardHeader>
                <CardContent className="space-y-3">
                  <button
                    type="button"
                    onClick={() => seller && navigate(`/users/${seller.id}`)}
                    disabled={!seller}
                    className="w-full rounded-md border bg-muted/30 p-3 text-left text-sm transition-colors hover:bg-muted disabled:cursor-default disabled:hover:bg-muted/30"
                  >
                    <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Seller
                    </div>
                    <div className="mt-1 font-medium">
                      {seller ? `${seller.first_name} ${seller.last_name}` : "Unknown"}
                    </div>
                    {seller?.email && (
                      <div className="text-xs text-muted-foreground">
                        {seller.email}
                      </div>
                    )}
                    {seller && (
                      <div className="mt-1 text-[10px] text-primary">
                        View profile →
                      </div>
                    )}
                  </button>

                  {isOwnListing ? (
                    <div className="rounded-md border border-dashed px-3 py-2 text-xs text-muted-foreground">
                      This is your listing. Edit it from the My Listings tab.
                    </div>
                  ) : startedConversationId ? (
                    <div className="flex items-start gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
                      <div>
                        Conversation started. Check your inbox to continue the
                        thread.
                      </div>
                    </div>
                  ) : (
                    <>
                      <Button
                        className="w-full"
                        onClick={() => setComposerOpen((o) => !o)}
                      >
                        <MessageSquare className="mr-2 h-4 w-4" />
                        Contact seller
                      </Button>
                      <div
                        className={cn(
                          "space-y-2 overflow-hidden transition-all",
                          composerOpen ? "max-h-96" : "max-h-0",
                        )}
                      >
                        <Textarea
                          placeholder="Leave blank to send an auto-generated opener..."
                          value={initialMessage}
                          onChange={(e) => setInitialMessage(e.target.value)}
                          disabled={startConversation.isPending}
                        />
                        {contactError && (
                          <div className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive">
                            {contactError}
                          </div>
                        )}
                        <Button
                          className="w-full"
                          variant="secondary"
                          size="sm"
                          onClick={() => startConversation.mutate()}
                          disabled={startConversation.isPending}
                        >
                          {startConversation.isPending ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Sending...
                            </>
                          ) : (
                            "Send message"
                          )}
                        </Button>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Leave a review — shown for sold listings where user was involved */}
              {listing.status === "sold" && !isOwnListing && (
                <ReviewForm
                  listingId={listing.id}
                  reviewedUserId={listing.seller_id}
                  reviewedName={seller ? `${seller.first_name} ${seller.last_name}` : "Seller"}
                />
              )}
              {listing.status === "sold" && isOwnListing && (
                <ReviewForm
                  listingId={listing.id}
                  reviewedUserId={null}
                  reviewedName="the buyer"
                  isSeller
                />
              )}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function ReviewForm({ listingId, reviewedUserId, reviewedName, isSeller = false }) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const submitReview = useMutation({
    mutationFn: () =>
      reviewsApi.create({
        reviewed_user_id: reviewedUserId,
        listing_id: listingId,
        rating,
        comment: comment.trim() || null,
      }),
    onSuccess: () => setSubmitted(true),
    onError: (err) =>
      setError(err instanceof ApiError ? err.message : "Failed to submit review"),
  });

  if (submitted) {
    return (
      <Card>
        <CardContent className="flex items-center gap-2 py-6 text-sm text-emerald-700">
          <CheckCircle2 className="h-4 w-4" />
          Review submitted! Thank you.
        </CardContent>
      </Card>
    );
  }

  // If seller view and we don't know the buyer ID, show a message
  if (isSeller && !reviewedUserId) {
    return (
      <Card>
        <CardContent className="py-4 text-xs text-muted-foreground">
          This listing has been sold. You can rate the buyer from their profile.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Rate {reviewedName}</CardTitle>
        <CardDescription className="text-xs">
          How was your experience with this transaction?
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Star rating */}
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoverRating(star)}
              onMouseLeave={() => setHoverRating(0)}
              className="p-0.5"
            >
              <Star
                className={cn(
                  "h-6 w-6 transition-colors",
                  (hoverRating || rating) >= star
                    ? "fill-amber-400 text-amber-400"
                    : "text-muted-foreground/30",
                )}
              />
            </button>
          ))}
          {rating > 0 && (
            <span className="ml-2 self-center text-sm text-muted-foreground">
              {rating}/5
            </span>
          )}
        </div>

        <Textarea
          placeholder="Optional comment about your experience..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="min-h-[60px]"
        />

        {error && (
          <div className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive">
            {error}
          </div>
        )}

        <Button
          size="sm"
          className="w-full"
          disabled={rating === 0 || submitReview.isPending}
          onClick={() => {
            setError(null);
            submitReview.mutate();
          }}
        >
          {submitReview.isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Submitting...
            </>
          ) : (
            "Submit review"
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

function InfoRow({ label, value }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div className="mt-0.5">{value}</div>
    </div>
  );
}
