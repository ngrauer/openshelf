import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Loader2,
  Pencil,
  Plus,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
import { listingsApi, textbooksApi, ApiError } from "@/lib/api";

const CONDITIONS = [
  { value: "new", label: "New" },
  { value: "like_new", label: "Like New" },
  { value: "good", label: "Good" },
  { value: "fair", label: "Fair" },
  { value: "poor", label: "Poor" },
];

function formatPrice(value) {
  if (value == null || value === "") return "—";
  return `$${Number(value).toFixed(2)}`;
}

export function MyListingsView() {
  const { user } = useAuth();
  const userId = user?.id;
  const queryClient = useQueryClient();

  // Active listings — backend has no seller_id filter yet, so we filter
  // client-side on the current user.
  const listingsQuery = useQuery({
    queryKey: ["my-listings", userId],
    queryFn: () => listingsApi.list({ status: "active" }),
    enabled: !!userId,
  });

  const mine = useMemo(
    () => (listingsQuery.data ?? []).filter((l) => l.seller_id === userId),
    [listingsQuery.data, userId],
  );

  // `null` = closed, "new" = create form open, <id> = editing that listing
  const [formMode, setFormMode] = useState(null);

  const deleteListing = useMutation({
    mutationFn: (id) => listingsApi.remove(id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["my-listings", userId] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Listings</h1>
          <p className="text-muted-foreground">
            Manage the textbooks you're selling.
          </p>
        </div>
        {formMode !== "new" && (
          <Button onClick={() => setFormMode("new")}>
            <Plus className="mr-2 h-4 w-4" />
            New listing
          </Button>
        )}
      </div>

      {formMode === "new" && (
        <ListingForm
          mode="create"
          onClose={() => setFormMode(null)}
          onSaved={() => {
            setFormMode(null);
            queryClient.invalidateQueries({ queryKey: ["my-listings", userId] });
          }}
        />
      )}

      {listingsQuery.isLoading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading your listings...
        </div>
      ) : mine.length === 0 && formMode !== "new" ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            You haven't listed any textbooks yet. Click{" "}
            <span className="font-medium">New listing</span> to get started.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {mine.map((listing) =>
            formMode === listing.id ? (
              <ListingForm
                key={listing.id}
                mode="edit"
                listing={listing}
                onClose={() => setFormMode(null)}
                onSaved={() => {
                  setFormMode(null);
                  queryClient.invalidateQueries({
                    queryKey: ["my-listings", userId],
                  });
                }}
              />
            ) : (
              <MyListingRow
                key={listing.id}
                listing={listing}
                onEdit={() => setFormMode(listing.id)}
                onDelete={() => {
                  if (confirm(`Delete "${listing.textbook?.title}"?`)) {
                    deleteListing.mutate(listing.id);
                  }
                }}
                deleting={
                  deleteListing.isPending &&
                  deleteListing.variables === listing.id
                }
              />
            ),
          )}
        </div>
      )}
    </div>
  );
}

function MyListingRow({ listing, onEdit, onDelete, deleting }) {
  const tb = listing.textbook;
  return (
    <Card>
      <CardContent className="flex items-center justify-between gap-4 py-4">
        <div className="min-w-0 flex-1">
          <div className="truncate font-medium">{tb?.title ?? "Untitled"}</div>
          <div className="truncate text-xs text-muted-foreground">
            {tb?.author}
            {tb?.edition ? ` · ${tb.edition}` : ""}
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold">
            {formatPrice(listing.price)}
          </div>
          {listing.ai_recommended_price != null && (
            <div className="flex items-center justify-end gap-1 text-[10px] text-muted-foreground">
              <Sparkles className="h-3 w-3" />
              AI {formatPrice(listing.ai_recommended_price)}
            </div>
          )}
        </div>
        <div className="flex gap-1">
          <Button variant="ghost" size="icon" onClick={onEdit}>
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onDelete}
            disabled={deleting}
          >
            {deleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function ListingForm({ mode, listing, onClose, onSaved }) {
  const isEdit = mode === "edit";

  const [textbookId, setTextbookId] = useState(
    listing?.textbook_id?.toString() ?? "",
  );
  const [condition, setCondition] = useState(listing?.condition ?? "good");
  const [price, setPrice] = useState(
    listing?.price != null ? String(listing.price) : "",
  );
  const [description, setDescription] = useState(listing?.description ?? "");
  const [error, setError] = useState(null);

  // Textbook dropdown data. Only needed in create mode, but we fetch
  // unconditionally so the form can still render the current book name
  // in edit mode even if the listing comes in without a nested textbook.
  const textbooksQuery = useQuery({
    queryKey: ["textbooks"],
    queryFn: () => textbooksApi.list(),
  });

  // Live AI price suggestion. Debounced so we don't hammer the endpoint
  // as the user tabs through fields. Refetches whenever (textbookId,
  // condition) changes.
  const [debounced, setDebounced] = useState({ textbookId, condition });
  useEffect(() => {
    const t = setTimeout(
      () => setDebounced({ textbookId, condition }),
      300,
    );
    return () => clearTimeout(t);
  }, [textbookId, condition]);

  const aiPriceQuery = useQuery({
    queryKey: ["ai-price", debounced.textbookId, debounced.condition],
    queryFn: () =>
      listingsApi.aiPrice(Number(debounced.textbookId), debounced.condition),
    enabled: !!debounced.textbookId && !!debounced.condition,
  });

  const saveListing = useMutation({
    mutationFn: () => {
      if (isEdit) {
        return listingsApi.update(listing.id, {
          condition,
          price: Number(price),
          description: description || null,
        });
      }
      return listingsApi.create({
        textbook_id: Number(textbookId),
        condition,
        price: Number(price),
        description: description || null,
      });
    },
    onSuccess: () => onSaved?.(),
    onError: (err) =>
      setError(err instanceof ApiError ? err.message : "Save failed"),
  });

  function submit(e) {
    e.preventDefault();
    setError(null);
    if (!isEdit && !textbookId) {
      setError("Pick a textbook");
      return;
    }
    if (!price || Number(price) <= 0) {
      setError("Enter a valid price");
      return;
    }
    saveListing.mutate();
  }

  const suggested = aiPriceQuery.data?.recommended_price;
  const currentPriceNum = Number(price);
  const priceVsAi =
    suggested != null && currentPriceNum > 0
      ? currentPriceNum > suggested * 1.15
        ? "high"
        : currentPriceNum < suggested * 0.85
          ? "low"
          : "ok"
      : null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <div>
          <CardTitle>{isEdit ? "Edit listing" : "New listing"}</CardTitle>
          <CardDescription>
            {isEdit
              ? "Update condition, price, or description."
              : "Pick a textbook and set your price."}
          </CardDescription>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="textbook">Textbook</Label>
            {isEdit ? (
              <div className="rounded-md border bg-muted/30 px-3 py-2 text-sm">
                {listing?.textbook?.title ?? `Textbook #${listing?.textbook_id}`}
              </div>
            ) : (
              <select
                id="textbook"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                value={textbookId}
                onChange={(e) => setTextbookId(e.target.value)}
                disabled={textbooksQuery.isLoading}
                required
              >
                <option value="">Select a textbook...</option>
                {(textbooksQuery.data ?? []).map((tb) => (
                  <option key={tb.id} value={tb.id}>
                    {tb.title} — {tb.author}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="condition">Condition</Label>
              <select
                id="condition"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
              >
                {CONDITIONS.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="price">Price (USD)</Label>
              <Input
                id="price"
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
              />
            </div>
          </div>

          {textbookId && (
            <div className="rounded-md border bg-muted/20 p-3 text-xs">
              <div className="flex items-center gap-2 font-medium">
                <Sparkles className="h-3 w-3 text-primary" />
                AI price suggestion
              </div>
              <div className="mt-1 text-muted-foreground">
                {aiPriceQuery.isLoading ? (
                  "Calculating..."
                ) : suggested != null ? (
                  <>
                    Recommended{" "}
                    <span className="font-semibold text-foreground">
                      {formatPrice(suggested)}
                    </span>
                    {aiPriceQuery.data?.reasoning && (
                      <span> — {aiPriceQuery.data.reasoning}</span>
                    )}
                  </>
                ) : (
                  "No recommendation available."
                )}
              </div>
              {priceVsAi === "high" && (
                <div className="mt-1 text-amber-700">
                  Your price is noticeably above the recommendation.
                </div>
              )}
              {priceVsAi === "low" && (
                <div className="mt-1 text-emerald-700">
                  Your price is below the recommendation — likely to sell fast.
                </div>
              )}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Highlights, highlighting, missing pages, etc."
            />
          </div>

          {error && (
            <div className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={saveListing.isPending}>
              {saveListing.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : isEdit ? (
                "Save changes"
              ) : (
                "Publish listing"
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

