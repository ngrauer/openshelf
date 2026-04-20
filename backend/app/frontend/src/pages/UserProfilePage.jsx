import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Star, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { DashboardLayout, DASHBOARD_VIEWS } from "@/components/DashboardLayout";
import { reviewsApi } from "@/lib/api";
import { cn } from "@/lib/utils";

function Stars({ rating, size = "h-4 w-4" }) {
  const full = Math.round(rating ?? 0);
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          className={cn(
            size,
            n <= full
              ? "fill-amber-400 text-amber-400"
              : "text-muted-foreground",
          )}
        />
      ))}
    </div>
  );
}

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function UserProfilePage() {
  const { id } = useParams();
  const userId = Number(id);
  const navigate = useNavigate();

  const profileQuery = useQuery({
    queryKey: ["user-profile", userId],
    queryFn: () => reviewsApi.profile(userId),
    enabled: Number.isFinite(userId),
  });

  const reviewsQuery = useQuery({
    queryKey: ["user-reviews", userId],
    queryFn: () => reviewsApi.forUser(userId),
    enabled: Number.isFinite(userId),
  });

  const profile = profileQuery.data;
  const reviews = reviewsQuery.data ?? [];

  return (
    <DashboardLayout
      view={DASHBOARD_VIEWS.SHOPPING}
      onViewChange={(next) => navigate(`/?view=${next}`)}
      onOpenChat={() => {}}
    >
      <div className="mx-auto max-w-3xl space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(-1)}
          className="-ml-2"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        {profileQuery.isLoading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading profile...
          </div>
        )}

        {profile && (
          <Card>
            <CardHeader className="flex flex-row items-start gap-4 space-y-0">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-lg font-semibold text-primary">
                {profile.first_name?.[0]}
                {profile.last_name?.[0]}
              </div>
              <div className="flex-1">
                <CardTitle className="text-2xl">
                  {profile.first_name} {profile.last_name}
                </CardTitle>
                <CardDescription>{profile.email}</CardDescription>
                <div className="mt-2 flex items-center gap-3">
                  {profile.average_rating != null ? (
                    <div className="flex items-center gap-2">
                      <Stars rating={profile.average_rating} />
                      <span className="text-sm font-medium">
                        {profile.average_rating.toFixed(1)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        ({profile.total_reviews} review
                        {profile.total_reviews === 1 ? "" : "s"})
                      </span>
                    </div>
                  ) : (
                    <span className="text-xs text-muted-foreground">
                      No reviews yet
                    </span>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
                <Stat
                  icon={Tag}
                  label="Active listings"
                  value={profile.active_listings}
                />
                <Stat
                  icon={Star}
                  label="Avg rating"
                  value={
                    profile.average_rating != null
                      ? profile.average_rating.toFixed(1)
                      : "—"
                  }
                />
                <Stat
                  icon={Star}
                  label="Total reviews"
                  value={profile.total_reviews}
                />
              </div>
            </CardContent>
          </Card>
        )}

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Reviews</h2>
          {reviewsQuery.isLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading reviews...
            </div>
          ) : reviews.length === 0 ? (
            <Card>
              <CardContent className="py-10 text-center text-sm text-muted-foreground">
                No reviews yet.
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {reviews.map((r) => (
                <Card key={r.id}>
                  <CardContent className="space-y-2 py-4">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-medium">
                        {r.reviewer
                          ? `${r.reviewer.first_name} ${r.reviewer.last_name}`
                          : "Anonymous"}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatDate(r.created_at)}
                      </div>
                    </div>
                    <Stars rating={r.rating} size="h-3.5 w-3.5" />
                    {r.comment && (
                      <p className="text-sm text-muted-foreground">
                        {r.comment}
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="rounded-md border bg-muted/20 p-3">
      <div className="flex items-center gap-1 text-xs text-muted-foreground">
        <Icon className="h-3 w-3" />
        {label}
      </div>
      <div className="mt-1 text-xl font-semibold">{value ?? "—"}</div>
    </div>
  );
}
