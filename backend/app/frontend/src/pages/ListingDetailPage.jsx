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
import { conversationsApi, listingsApi, ApiError } from "@/lib/api";
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
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
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
