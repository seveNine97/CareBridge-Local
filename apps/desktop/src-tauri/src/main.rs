#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::{Mutex, OnceLock};

static LOCAL_CORE_CHILD: OnceLock<Mutex<Option<Child>>> = OnceLock::new();

fn local_core_state() -> &'static Mutex<Option<Child>> {
    LOCAL_CORE_CHILD.get_or_init(|| Mutex::new(None))
}

fn resolve_home_dir() -> PathBuf {
    if let Ok(value) = env::var("LOCALAPPDATA") {
        return PathBuf::from(value).join("CareBridgeLocal");
    }
    env::current_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
        .join(".carebridge")
}

fn resolve_sidecar_path() -> Option<PathBuf> {
    let exe = env::current_exe().ok()?;
    let exe_dir = exe.parent()?;
    let bundled = exe_dir
        .join("resources")
        .join("local-core")
        .join("carebridge-local-core.exe");
    if bundled.exists() {
        return Some(bundled);
    }
    let dev_candidate = Path::new("../../../../scripts/dist/carebridge-local-core.exe");
    if dev_candidate.exists() {
        return Some(dev_candidate.canonicalize().ok()?);
    }
    None
}

fn start_local_core() {
    let sidecar = match resolve_sidecar_path() {
        Some(path) => path,
        None => return,
    };
    let home_dir = resolve_home_dir();
    let _ = std::fs::create_dir_all(&home_dir);

    let knowledge_root = env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|x| x.to_path_buf()))
        .map(|dir| dir.join("resources").join("knowledge-packs"));
    let runtime_bundle = env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|x| x.to_path_buf()))
        .map(|dir| dir.join("resources").join("runtime").join("llama.cpp"));

    let mut command = Command::new(sidecar);
    command
        .env("CAREBRIDGE_HOME", home_dir.as_os_str())
        .env("CAREBRIDGE_HOST", "127.0.0.1")
        .env("CAREBRIDGE_PORT", "8011")
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    if let Some(path) = knowledge_root {
        command.env("CAREBRIDGE_KNOWLEDGE_ROOT", path.as_os_str());
    }
    if let Some(path) = runtime_bundle {
        command.env("CAREBRIDGE_RUNTIME_BUNDLE", path.as_os_str());
    }
    if let Ok(mut child_slot) = local_core_state().lock() {
        if child_slot.is_none() {
            if let Ok(child) = command.spawn() {
                *child_slot = Some(child);
            }
        }
    }
}

fn stop_local_core() {
    if let Ok(mut child_slot) = local_core_state().lock() {
        if let Some(mut child) = child_slot.take() {
            let _ = child.kill();
        }
    }
}

fn main() {
    let result = tauri::Builder::default()
        .setup(|_| {
            start_local_core();
            Ok(())
        })
        .run(tauri::generate_context!());

    stop_local_core();

    result.expect("error while running carebridge desktop");
}
