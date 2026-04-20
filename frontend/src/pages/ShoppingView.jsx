import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BookMarked, CalendarDays, ChevronDown, ChevronRight,
  Loader2, RefreshCw, Search, Sparkles, X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ListingCard } from "@/components/ListingCard";
import { useAuth } from "@/contexts/AuthContext";
import { coursesApi, listingsApi, matchesApi } from "@/lib/api";

export function ShoppingView() {
  const { user } = useAuth();
  const userId = user?.id;
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [activeCourseId, setActiveCourseId] = useState(null);
  const [extraCourses, setExtraCourses] = useState([]);
  const [courseSearchQ, setCourseSearchQ] = useState("");
  const [courseSearchFocused, setCourseSearchFocused] = useState(false);
  const [debouncedCourseQ, setDebouncedCourseQ] = useState("");
  const [expandedCourse, setExpandedCourse] = useState(null);
  const courseSearchRef = useRef(null);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedCourseQ(courseSearchQ), 300);
    return () => clearTimeout(t);
  }, [courseSearchQ]);

  const enrollmentsQuery = useQuery({
    queryKey: ["enrollments", userId],
    queryFn: () => coursesApi.enrollments(userId),
    enabled: !!userId,
  });

  const matchesQuery = useQuery({
    queryKey: ["matches", userId],
    queryFn: () => matchesApi.get(userId),
    enabled: !!userId,
  });

  const generateMatches = useMutation({
    mutationFn: () => matchesApi.generate(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["matches", userId] }),
  });

  const courseSearchQuery = useQuery({
    queryKey: ["course-search", debouncedCourseQ, user?.university_id],
    queryFn: () => coursesApi.search(debouncedCourseQ, user?.university_id),
    enabled: debouncedCourseQ.length >= 2,
  });

  const listingsQuery = useQuery({
    queryKey: ["listings", { search, course_id: activeCourseId }],
    queryFn: () =>
      listingsApi.list({
        title: search || undefined,
        course_id: activeCourseId || undefined,
      }),
  });

  const courses = enrollmentsQuery.data ?? [];
  const matches = matchesQuery.data ?? [];
  const listings = listingsQuery.data ?? [];

  const visibleListings = useMemo(
    () => listings.filter((l) => l.seller_id !== userId),
    [listings, userId],
  );
  const visibleMatches = useMemo(
    () => matches.filter((m) => m.listing?.seller_id !== userId),
    [matches, userId],
  );

  const enrolledCourseIds = useMemo(
    () => new Set(courses.map((e) => e.course_id)),
    [courses],
  );

  const allChips = useMemo(() => {
    const chips = courses.map((e) => ({
      id: e.course_id,
      code: e.course?.course_code ?? `Course ${e.course_id}`,
      name: e.course?.course_name ?? "",
      isExtra: false,
    }));
    extraCourses
      .filter((ec) => !enrolledCourseIds.has(ec.id))
      .forEach((ec) => chips.push({ ...ec, isExtra: true }));
    return chips;
  }, [courses, extraCourses, enrolledCourseIds]);

  function selectCourse(id) {
    setActiveCourseId((prev) => (prev === id ? null : id));
  }

  function addExtraCourse(course) {
    setExtraCourses((prev) =>
      prev.find((c) => c.id === course.id) ? prev : [...prev, { id: course.id, code: course.course_code, name: course.course_name }],
    );
    setActiveCourseId(course.id);
    setCourseSearchQ("");
  }

  function removeExtraCourse(courseId) {
    setExtraCourses((prev) => prev.filter((c) => c.id !== courseId));
    if (activeCourseId === courseId) setActiveCourseId(null);
  }

  const showDropdown =
    courseSearchFocused &&
    debouncedCourseQ.length >= 2 &&
    (courseSearchQuery.data?.length ?? 0) > 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Shopping</h1>
          <p className="text-muted-foreground">
            Find textbooks for your courses.
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

      {/* My Course Schedule */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <CalendarDays className="h-4 w-4" />
            My Course Schedule
          </CardTitle>
          <CardDescription>
            Your enrolled courses and required textbooks. Click a textbook to search for listings.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {enrollmentsQuery.isLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading courses...
            </div>
          ) : courses.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              You're not enrolled in any courses this semester.
            </p>
          ) : (
            courses.map((enr) => {
              const c = enr.course;
              return (
                <CourseExpandable
                  key={enr.id}
                  courseId={enr.course_id}
                  code={c?.course_code ?? `Course ${enr.course_id}`}
                  name={c?.course_name ?? ""}
                  professor={c?.professor}
                  isExpanded={expandedCourse === enr.course_id}
                  onToggle={() =>
                    setExpandedCourse(
                      expandedCourse === enr.course_id ? null : enr.course_id,
                    )
                  }
                  onFindListings={(tb) => {
                    setSearch(tb.title);
                    setActiveCourseId(null);
                    setTimeout(() => {
                      document
                        .getElementById("browse-listings")
                        ?.scrollIntoView({ behavior: "smooth" });
                    }, 50);
                  }}
                />
              );
            })
          )}
        </CardContent>
      </Card>

      {/* AI matches */}
      {visibleMatches.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <h2 className="text-lg font-semibold">Matched for you</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {visibleMatches.slice(0, 6).map((m) => (
              <ListingCard key={m.id} listing={m.listing} matchScore={m.match_score} />
            ))}
          </div>
        </section>
      )}

      {/* Browse listings */}
      <section id="browse-listings" className="space-y-4">
        <h2 className="text-lg font-semibold">Browse listings</h2>

        {/* Course filter chips */}
        {allChips.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <FilterChip active={!activeCourseId} onClick={() => setActiveCourseId(null)}>
              All courses
            </FilterChip>
            {allChips.map((c) => (
              <FilterChip
                key={c.id}
                active={activeCourseId === c.id}
                onClick={() => selectCourse(c.id)}
              >
                {c.code}{c.name ? ` — ${c.name}` : ""}
                {c.isExtra && (
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={(e) => { e.stopPropagation(); removeExtraCourse(c.id); }}
                    onKeyDown={(e) => e.key === "Enter" && removeExtraCourse(c.id)}
                    className="ml-1.5 inline-flex items-center opacity-70 hover:opacity-100"
                  >
                    <X className="h-3 w-3" />
                  </span>
                )}
              </FilterChip>
            ))}
          </div>
        )}

        {/* Course search (any course) */}
        <div className="relative" ref={courseSearchRef}>
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={courseSearchQ}
            onChange={(e) => setCourseSearchQ(e.target.value)}
            onFocus={() => setCourseSearchFocused(true)}
            onBlur={() => setTimeout(() => setCourseSearchFocused(false), 200)}
            placeholder="Filter by any course (e.g. 'CS 301', 'Biology')..."
            className="pl-9"
          />
          {showDropdown && (
            <div className="absolute top-full z-20 mt-1 w-full rounded-md border bg-popover shadow-md">
              {courseSearchQuery.data.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onMouseDown={() => addExtraCourse(c)}
                  className="flex w-full items-start gap-2 px-3 py-2 text-left text-sm hover:bg-muted"
                >
                  <span className="font-medium">{c.course_code}</span>
                  <span className="text-muted-foreground">{c.course_name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Title/ISBN search */}
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title, author, or ISBN..."
            className="pl-9"
          />
        </div>

        {/* Listing grid */}
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
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium transition-colors " +
        (active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border bg-background text-muted-foreground hover:bg-muted")
      }
    >
      {children}
    </button>
  );
}

function CourseExpandable({
  courseId, code, name, professor, isExpanded, onToggle, onFindListings,
}) {
  const textbooksQuery = useQuery({
    queryKey: ["course-textbooks", courseId],
    queryFn: () => coursesApi.withTextbooks(courseId),
    enabled: isExpanded,
  });

  const textbooks = textbooksQuery.data?.textbooks ?? [];

  return (
    <div className="rounded-lg border">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between px-4 py-3 text-left text-sm hover:bg-muted/50"
      >
        <div>
          <span className="font-medium">{code}</span>
          <span className="ml-2 text-muted-foreground">{name}</span>
          {professor && (
            <span className="ml-2 text-xs text-muted-foreground">({professor})</span>
          )}
        </div>
        {isExpanded ? (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        )}
      </button>
      {isExpanded && (
        <div className="border-t px-4 py-3">
          {textbooksQuery.isLoading ? (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-3 w-3 animate-spin" /> Loading textbooks...
            </div>
          ) : textbooks.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No textbooks assigned to this course.
            </p>
          ) : (
            <div className="space-y-3">
              {textbooks.map((tb) => (
                <div key={tb.id} className="flex items-center gap-3">
                  {tb.image_url ? (
                    <img
                      src={tb.image_url}
                      alt={tb.title}
                      className="h-10 w-8 rounded border object-cover"
                    />
                  ) : (
                    <div className="flex h-10 w-8 shrink-0 items-center justify-center rounded border bg-muted">
                      <BookMarked className="h-4 w-4 text-muted-foreground/40" />
                    </div>
                  )}
                  <div className="min-w-0 flex-1 text-sm">
                    <div className="truncate font-medium">{tb.title}</div>
                    <div className="truncate text-xs text-muted-foreground">
                      {tb.author}
                      {tb.edition ? ` · ${tb.edition}` : ""}
                      {tb.retail_price ? ` · $${tb.retail_price.toFixed(2)}` : ""}
                    </div>
                  </div>
                  {onFindListings && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="shrink-0 text-xs"
                      onClick={() => onFindListings(tb)}
                    >
                      Find listings
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
