import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ImagePlus,
  Loader2,
  Pencil,
  Plus,
  Sparkles,
  Trash2,
  Upload,
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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
import { listingsApi, textbooksApi, uploadsApi, ApiError } from "@/lib/api";

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

  const listingsQuery = useQuery({
    queryKey: ["my-listings", userId],
    queryFn: () => listingsApi.list({ status: "active" }),
    enabled: !!userId,
  });

  const mine = useMemo(
    () => (listingsQuery.data ?? []).filter((l) => l.seller_id === userId),
    [listingsQuery.data, userId],
  );

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
  const firstImage = listing.image_urls?.[0] ?? listing.image_url;
  return (
    <Card>
      <CardContent className="flex items-center justify-between gap-4 py-4">
        {firstImage && (
          <img
            src={firstImage}
            alt={tb?.title}
            className="h-12 w-10 shrink-0 rounded border object-cover"
          />
        )}
        <div className="min-w-0 flex-1">
          <div className="truncate font-medium">{tb?.title ?? "Untitled"}</div>
          <div className="truncate text-xs text-muted-foreground">
            {tb?.author}
            {tb?.edition ? ` · ${tb.edition}` : ""}
            {listing.image_urls?.length > 1 && (
              <span className="ml-2 text-[10px]">
                {listing.image_urls.length} photos
              </span>
            )}
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
  const fileInputRef = useRef(null);

  const [textbookId, setTextbookId] = useState(
    listing?.textbook_id?.toString() ?? "",
  );
  const [condition, setCondition] = useState(listing?.condition ?? "good");
  const [price, setPrice] = useState(
    listing?.price != null ? String(listing.price) : "",
  );
  const [description, setDescription] = useState(listing?.description ?? "");
  const [imageUrls, setImageUrls] = useState(() => {
    if (listing?.image_urls?.length) return listing.image_urls;
    if (listing?.image_url) return [listing.image_url];
    return [];
  });
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const textbooksQuery = useQuery({
    queryKey: ["textbooks"],
    queryFn: () => textbooksApi.list(),
  });

  const [debounced, setDebounced] = useState({ textbookId, condition });
  useEffect(() => {
    const t = setTimeout(() => setDebounced({ textbookId, condition }), 300);
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
      const payload = {
        condition,
        price: Number(price),
        description: description || null,
        image_url: imageUrls[0] || null,
        image_urls: imageUrls,
      };
      if (isEdit) return listingsApi.update(listing.id, payload);
      return listingsApi.create({ textbook_id: Number(textbookId), ...payload });
    },
    onSuccess: () => onSaved?.(),
    onError: (err) =>
      setError(err instanceof ApiError ? err.message : "Save failed"),
  });

  async function uploadFiles(files) {
    const remaining = 5 - imageUrls.length;
    if (remaining <= 0) return;
    const toUpload = Array.from(files).slice(0, remaining);
    setUploading(true);
    try {
      const results = await Promise.all(toUpload.map((f) => uploadsApi.upload(f)));
      setImageUrls((prev) => [...prev, ...results.map((r) => r.url)].slice(0, 5));
    } catch {
      setError("Image upload failed");
    } finally {
      setUploading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.length) uploadFiles(e.dataTransfer.files);
  }

  function removeImage(idx) {
    setImageUrls((prev) => prev.filter((_, i) => i !== idx));
  }

  function submit(e) {
    e.preventDefault();
    setError(null);
    if (!isEdit && !textbookId) { setError("Pick a textbook"); return; }
    if (!price || Number(price) <= 0) { setError("Enter a valid price"); return; }
    saveListing.mutate();
  }

  const suggested = aiPriceQuery.data?.recommended_price;
  const currentPriceNum = Number(price);
  const priceVsAi =
    suggested != null && currentPriceNum > 0
      ? currentPriceNum > suggested * 1.15 ? "high"
      : currentPriceNum < suggested * 0.85 ? "low"
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

          {/* Textbook */}
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

          {/* Condition + Price */}
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
              <input
                id="price"
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>

          {/* AI price suggestion */}
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
                  <div className="flex items-center gap-2">
                    <span>
                      Recommended{" "}
                      <span className="font-semibold text-foreground">
                        {formatPrice(suggested)}
                      </span>
                      {aiPriceQuery.data?.reasoning && (
                        <span> — {aiPriceQuery.data.reasoning}</span>
                      )}
                    </span>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      className="h-6 px-2 text-[10px]"
                      onClick={() => setPrice(suggested.toFixed(2))}
                    >
                      Use this price
                    </Button>
                  </div>
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

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Highlights, highlighting, missing pages, etc."
            />
          </div>

          {/* Photos */}
          <div className="space-y-2">
            <Label>Photos (optional, up to 5)</Label>

            {/* Drag-and-drop zone */}
            <div
              role="button"
              tabIndex={0}
              onClick={() => imageUrls.length < 5 && fileInputRef.current?.click()}
              onKeyDown={(e) => e.key === "Enter" && imageUrls.length < 5 && fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className={
                "flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 transition-colors " +
                (isDragging
                  ? "border-primary bg-primary/5"
                  : imageUrls.length >= 5
                    ? "cursor-not-allowed border-border opacity-50"
                    : "cursor-pointer border-border hover:border-primary/50 hover:bg-muted/30")
              }
            >
              {uploading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <Upload className="h-6 w-6 text-muted-foreground" />
              )}
              <div className="text-center">
                <p className="text-sm font-medium">
                  {uploading
                    ? "Uploading..."
                    : imageUrls.length >= 5
                      ? "Maximum 5 photos reached"
                      : "Drag photos here or click to upload"}
                </p>
                <p className="text-xs text-muted-foreground">
                  JPG, PNG, WebP — max 5 MB each
                </p>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(e) => e.target.files?.length && uploadFiles(e.target.files)}
            />

            {/* Thumbnail previews */}
            {imageUrls.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {imageUrls.map((url, idx) => (
                  <div key={url} className="relative">
                    <img
                      src={url}
                      alt={`Photo ${idx + 1}`}
                      className="h-20 w-20 rounded-md border object-cover"
                    />
                    {idx === 0 && (
                      <span className="absolute bottom-0 left-0 rounded-bl-md rounded-tr-md bg-black/60 px-1 text-[9px] text-white">
                        Main
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => removeImage(idx)}
                      className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-destructive-foreground shadow"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
                {imageUrls.length < 5 && (
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex h-20 w-20 items-center justify-center rounded-md border-2 border-dashed border-border text-muted-foreground hover:border-primary/50 hover:bg-muted/30"
                  >
                    <ImagePlus className="h-5 w-5" />
                  </button>
                )}
              </div>
            )}
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
