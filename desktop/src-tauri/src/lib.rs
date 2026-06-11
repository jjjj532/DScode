use std::path::Path;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::Duration;

use tauri::Manager;

struct BackendState {
    child: Option<Child>,
    port: u16,
}

impl BackendState {
    fn new(port: u16) -> Self {
        Self { child: None, port }
    }

    fn start(&mut self, resource_dir: Option<&Path>) -> Result<(), String> {
        let bundled = resource_dir
            .map(|d| d.join("binaries").join("cscode-server"))
            .filter(|p| p.exists());

        let mut cmd = if let Some(bin) = bundled {
            let mut c = Command::new(bin);
            c.args(["--port", &self.port.to_string(), "--host", "127.0.0.1"]);
            c
        } else {
            let mut c = Command::new("python3");
            c.args([
                "-m",
                "cscode",
                "server",
                "--port",
                &self.port.to_string(),
                "--host",
                "127.0.0.1",
            ]);
            c
        };

        let child = cmd
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .map_err(|e| format!("Failed to start backend: {e}"))?;

        self.child = Some(child);
        Ok(())
    }

    fn stop(&mut self) {
        if let Some(ref mut child) = self.child {
            let _ = child.kill();
            let _ = child.wait();
            self.child = None;
        }
    }
}

async fn wait_for_health(port: u16) -> Result<(), String> {
    let url = format!("http://127.0.0.1:{port}/api/health");
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {e}"))?;

    for _ in 0..50 {
        match client.get(&url).send().await {
            Ok(resp) if resp.status().is_success() => return Ok(()),
            _ => tokio::time::sleep(Duration::from_millis(200)).await,
        }
    }
    Err(format!("Backend at {url} did not become ready within 10 seconds"))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let port: u16 = 8080;
    let mut backend = BackendState::new(port);

    tauri::Builder::default()
        .setup(move |app| {
            let resource_dir = app.path().resource_dir().ok();

            // Start backend (tries bundled binary first, falls back to python3)
            if let Err(e) = backend.start(resource_dir.as_deref()) {
                eprintln!("{e}");
            }

            let window = app.get_webview_window("main").ok_or("no main window")?;

            tauri::async_runtime::spawn(async move {
                match wait_for_health(port).await {
                    Ok(()) => {
                        let url = url::Url::parse(&format!("http://127.0.0.1:{port}"))
                            .expect("invalid URL");
                        let _ = window.navigate(url);
                    }
                    Err(e) => {
                        eprintln!("{e}");
                    }
                }
            });

            app.manage(Mutex::new(backend));

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if let Some(state) = window.try_state::<Mutex<BackendState>>() {
                    if let Ok(mut backend) = state.lock() {
                        backend.stop();
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}
