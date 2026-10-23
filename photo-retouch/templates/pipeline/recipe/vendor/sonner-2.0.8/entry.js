// Sonner (Emil Kowalski) para el editor sin React: React, ReactDOM y Sonner en un solo archivo, sin red.
// window.Sonner.mount(el, props) monta un <Toaster>; window.Sonner.toast es el toast() de siempre.
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { Toaster, toast } from "sonner";
window.Sonner = { toast, mount(el, props) { createRoot(el).render(createElement(Toaster, props)); } };
