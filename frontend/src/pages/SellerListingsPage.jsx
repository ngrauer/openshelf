import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { DashboardLayout, DASHBOARD_VIEWS } from "@/components/DashboardLayout";
import { ListingCard } from "@/components/ListingCard";
import { listingsApi, reviewsApi } from "@/lib/api";

export function SellerListingsPage() {
  const { id } = useParams();
  const userId = Number(id);
  const navigate = useNavigate();

  const profileQuery = useQuery({
    queryKey: ["user-profile", userId],
    queryFn: () => reviewsApi.profile(userId),
    enabled: Number.isFinite(userId),
  });

  const listingsQuery = useQuery({
    queryKey: ["seller-listings", userId],
    queryFn: () => listingsApi.list({ seller_id: userId }),
    enabled: Number.isFinite(userId),
  });

  const profile = profileQuery.data;
  const listings = listingsQuery.data ?? [];

  return (
    <DashboardLayout
      view={DASHBOARD_VIEWS.SHOPPING}
      onViewChange={(next) => navigate(`/?view=${next}`)}
      onOpenChat={() => {}}
    >
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate(`/users/${userId}`)} className="-ml-2">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to profile
          </Button>
        </div>

        {profileQuery.isLoading ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading...
          </div>
        ) : profile ? (
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {profile.first_name} {profile.last_name}'s Listings
            </h1>
            <p className="text-muted-foreground flex items-center gap-1 mt-1">
              <Tag className="h-3.5 w-3.5" />
              {profile.active_listings} active listing{profile.active_listings === 1 ? "" : "s"}
            </p>
          </div>
        ) : null}

        {listingsQuery.isLoading ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading listings...
          </div>
        ) : listings.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-sm text-muted-foreground">
              This seller has no active listings.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {listings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
