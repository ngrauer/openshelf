import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookMarked, Loader2, RefreshCw, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ListingCard } from "@/components/ListingCard";
import { useAuth } from "@/contexts/AuthContext";
import { coursesApi, listingsApi, matchesApi } from "@/lib/api";

// The Shopping view pulls everything off the authenticated user — never
// a hardcoded id — so it "just works" for whoever signed in.
export function ShoppingView() {
  const { user } = useAuth();
  const userId = user?.id;
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [selectedCourseId, setSelectedCourseId] = useState(null);

  // Enrollments → courses the user is taking this semester.
  const enrollmentsQuery = useQuery({
    queryKey: ["enrollments", userId],
    queryFn: () => coursesApi.enrollments(userId),
    enabled: !!userId,
  });

  // Existing AI matches. Empty until the matching engine has been run.
  const matchesQuery = useQuery({
    queryKey: ["matches", userId],
    queryFn: () => matchesApi.get(userId),
    enabled: !!userId,
  });

  // Run the matching engine on-demand. Invalidates the matches query so
  // the grid updates once the server responds.
  const generateMatches = useMutation({
    mutationFn: () => matchesApi.generate(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["matches", userId] }),
  });

  // Filtered listing search. Fires whenever search text or course filter
  // changes. When both are empty, we still show active listings so the
  // grid is never blank.
  const listingsQuery = useQuery({
    queryKey: ["listings", { search, course_id: selectedCourseId }],
    queryFn: () =>
      listingsApi.list({
        title: search || undefined,
        course_id: selectedCourseId || undefined,
      }),
  });

  const courses = enrollmentsQuery.data ?? [];
  const matches = matchesQuery.data ?? [];
  const listings = listingsQuery.data ?? [];

  // Filter out the user's own listings from the shopping feed — you
  // can't buy from yourself. My Listings view (C6) is for those.
  const visibleListings = useMemo(
    () => listings.filter((l) => l.seller_id !== userId),
    [listings, userId],
  );
  const visibleMatches = useMemo(
    () => matches.filter((m) => m.listing && m.listing.seller_id !== userId),
    [matches, userId],
  );

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Shopping</h1>
          <p className="text-muted-foreground">
            Find textbooks for your enrolled courses.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => generateMatches.mutate()}
          disabled={generateMatches.isPending || !userId}
        >
          {generateMatches.isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-4 w-4" />
          )}
          Refresh matches
        </Button>
      </div>

      {/* Enrolled courses — double as filter chips for the search below. */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <BookMarked className="h-4 w-4" />
            Your courses
          </CardTitle>
          <CardDescription>
            Filter the listings grid to books required for one of your classes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {enrollmentsQuery.isLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading courses...
            </div>
          ) : courses.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              You're not enrolled in any courses this semester.
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              <FilterChip
                active={selectedCourseId == null}
                onClick={() => setSelectedCourseId(null)}
              >
                All
              </FilterChip>
              {courses.map((enr) => (
                <FilterChip
                  key={enr.id}
                  active={selectedCourseId === enr.course_id}
                  onClick={() => setSelectedCourseId(enr.course_id)}
                >
                  {enr.course?.course_code ?? `Course ${enr.course_id}`}
                </FilterChip>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI matches — only render the section if we have any. */}
      {visibleMatches.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <h2 className="text-lg font-semibold">Matched for you</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {visibleMatches.slice(0, 6).map((m) => (
              <ListingCard
                key={m.id}
                listing={m.listing}
                matchScore={m.match_score}
              />
            ))}
          </div>
        </section>
      )}

      {/* Free-text + course-filtered search grid. */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Browse listings</h2>
        </div>
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title..."
            className="pl-9"
          />
        </div>
        {listingsQuery.isLoading ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading listings...
          </div>
        ) : visibleListings.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-sm text-muted-foreground">
              No listings match your filters.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {visibleListings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function FilterChip({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        "rounded-full border px-3 py-1 text-xs font-medium transition-colors " +
        (active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border bg-background text-muted-foreground hover:bg-muted")
      }
    >
      {children}
    </button>
  );
}
