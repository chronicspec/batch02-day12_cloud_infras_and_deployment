import {
  Clock,
  MapPin,
  Navigation,
  Route,
  Tag,
  Users,
} from "lucide-react";
import type { ReactNode } from "react";
import { Facility, Navigation as NavType } from "../types";
import { cn } from "../lib/utils";

interface FacilityCardProps {
  facility: Facility;
  navigation?: NavType | null;
  isAlternative?: boolean;
}

const typeColors: Record<string, string> = {
  restaurant: "border-amber-200 bg-amber-50/90 text-amber-800",
  toilet: "border-sky-200 bg-sky-50/90 text-sky-800",
  first_aid: "border-red-200 bg-red-50/90 text-red-700",
  rest_area: "border-teal-200 bg-teal-50/90 text-teal-800",
  locker: "border-slate-300 bg-slate-100/90 text-slate-700",
  drinking_water: "border-cyan-200 bg-cyan-50/90 text-cyan-800",
  souvenir: "border-rose-200 bg-rose-50/90 text-rose-800",
  lost_found: "border-amber-200 bg-amber-50/90 text-amber-700",
  ticket_support: "border-indigo-200 bg-indigo-50/90 text-indigo-800",
};

const TYPE_LABELS: Record<string, string> = {
  restaurant: "Nhà hàng",
  toilet: "Nhà vệ sinh",
  first_aid: "Sơ cứu",
  rest_area: "Khu nghỉ chân",
  locker: "Tủ đồ",
  drinking_water: "Nước uống",
  souvenir: "Quà lưu niệm",
  lost_found: "Thất lạc",
  ticket_support: "Hỗ trợ vé",
};

const CROWD_LABELS: Record<string, string> = {
  low: "Thấp",
  medium: "Vừa",
  high: "Cao",
};

const TAG_LABELS: Record<string, string> = {
  vietnamese: "Món Việt",
  family: "Gia đình",
  kids_menu: "Thực đơn trẻ em",
  vegetarian: "Món chay",
  buffet: "Buffet",
  international: "Quốc tế",
  local: "Địa phương",
  traditional: "Truyền thống",
  korean: "Hàn Quốc",
  bbq: "Nướng",
  italian: "Ý",
  dessert: "Tráng miệng",
  chocolate: "Sô-cô-la",
  snack: "Ăn nhẹ",
  fast_food: "Đồ ăn nhanh",
  asian: "Món Á",
  european: "Món Âu",
  accessible: "Dễ tiếp cận",
  baby_care: "Chăm bé",
  shaded: "Có bóng mát",
  bench: "Ghế ngồi",
  ticket: "Vé",
  support: "Hỗ trợ",
  souvenir: "Lưu niệm",
};

function getTypeLabel(type: string): string {
  return TYPE_LABELS[type] ?? type.replace(/_/g, " ");
}

function getCrowdLabel(level: string): string {
  return CROWD_LABELS[level] ?? level;
}

function getTagLabel(tag: string): string {
  return TAG_LABELS[tag] ?? tag.replace(/_/g, " ");
}

export function FacilityCard({
  facility,
  navigation,
  isAlternative,
}: FacilityCardProps) {
  const tags = facility.tags.slice(0, isAlternative ? 2 : 4);

  return (
    <article
      className={cn(
        "overflow-hidden rounded-2xl border bg-white/[0.86] shadow-[0_18px_46px_rgba(15,23,42,0.12)] backdrop-blur-xl",
        isAlternative
          ? "border-white/70"
          : "border-amber-200/70 ring-1 ring-white/60",
      )}
    >
      <div className="p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span
                className={cn(
                  "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold shadow-sm",
                  typeColors[facility.type] ??
                    "border-slate-200 bg-slate-50 text-slate-700",
                )}
              >
                {getTypeLabel(facility.type)}
              </span>
              <span
                className={cn(
                  "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold",
                  facility.is_open
                    ? "bg-[linear-gradient(135deg,rgba(18,179,168,0.14),rgba(247,201,72,0.18))] text-vin-teal"
                    : "bg-slate-100 text-slate-500",
                )}
              >
                {facility.is_open ? "Đang mở" : "Tạm đóng"}
              </span>
            </div>
            <h3 className="text-base font-bold leading-snug text-slate-950">
              {facility.name}
            </h3>
            <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">
              {facility.description}
            </p>
          </div>

          {navigation && (
            <div className="grid min-w-[128px] grid-cols-2 overflow-hidden rounded-2xl border border-white/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(239,246,255,0.82))] text-center shadow-sm sm:grid-cols-1">
              <DistanceBlock label="Distance" value={`${navigation.distance_m}m`} />
              <DistanceBlock label="Walk" value={`${navigation.walk_time_min}m`} />
            </div>
          )}
        </div>

        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {navigation && (
            <>
              <Metric
                icon={<MapPin className="h-4 w-4" />}
                label="Origin"
                value={navigation.from_zone ?? "Current zone"}
              />
              <Metric
                icon={<Clock className="h-4 w-4" />}
                label="ETA"
                value={`${navigation.walk_time_min} phút`}
              />
            </>
          )}
          <Metric
            icon={<Users className="h-4 w-4" />}
            label="Crowd"
            value={getCrowdLabel(facility.crowd_level)}
          />
          <Metric
            icon={<Route className="h-4 w-4" />}
            label="Wait"
            value={`${facility.wait_time_min} phút`}
          />
        </div>

        {tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 rounded-full border border-white/70 bg-white/[0.72] px-2.5 py-1 text-xs font-semibold text-slate-600 shadow-sm"
              >
                <Tag className="h-3 w-3" />
                {getTagLabel(tag)}
              </span>
            ))}
          </div>
        )}
      </div>

      {navigation?.direction_text && !isAlternative && (
        <div className="border-t border-white/70 bg-[linear-gradient(135deg,rgba(239,246,255,0.86),rgba(240,253,250,0.72))] px-4 py-3">
          <div className="flex items-start gap-2 text-sm leading-6 text-slate-700">
            <Navigation className="mt-1 h-4 w-4 shrink-0 text-vin-teal" />
            <p>{navigation.direction_text}</p>
          </div>
        </div>
      )}
    </article>
  );
}

function DistanceBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-r border-white/70 px-3 py-2 last:border-r-0 sm:border-b sm:border-r-0 sm:last:border-b-0">
      <p className="text-lg font-black text-vin-blue">{value}</p>
      <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500">
        {label}
      </p>
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex min-w-0 items-center gap-3 rounded-xl border border-white/70 bg-white/[0.72] px-3 py-2 shadow-sm">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[linear-gradient(135deg,rgba(0,87,184,0.08),rgba(18,179,168,0.10))] text-vin-blue">
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
          {label}
        </p>
        <p className="truncate text-sm font-semibold text-slate-700">{value}</p>
      </div>
    </div>
  );
}
