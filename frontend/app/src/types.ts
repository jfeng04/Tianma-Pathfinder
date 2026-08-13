export type ObjectType =
  | "cylinder"
  | "box"
  | "gate";


export type Color =
  | "red"
  | "blue"
  | "yellow"
  | "green";


export type SpatialHint =
  | "nearest"
  | "farthest"
  | "far_end"
  | "left"
  | "right";


export type Constraint =
  | "avoid_obstacles"
  | "remain_in_course"
  | "do_not_enter_restricted_zone";


export interface Target {
  object_type: ObjectType;
  color: Color | null;
  spatial_hint: SpatialHint | null;
}


export interface Mission {
  action:
    | "navigate"
    | "inspect"
    | "return_to_start"
    | "stop";

  target: Target | null;

  stop_distance_m: number;

  constraints: Constraint[];
}

export interface TranscriptionResponse {
  text: string;
}