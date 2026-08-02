package com.finwise.app;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends Activity {

    private WebView webView;
    private FrameLayout root;
    private ProgressBar spinner;
    private TextView status;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(15, 23, 42));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setMediaPlaybackRequiresUserGesture(false);
        webView.setBackgroundColor(Color.rgb(15, 23, 42));
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                runOnUiThread(() -> root.removeView(spinner));
            }
        });
        webView.setWebChromeClient(new WebChromeClient());

        spinner = new ProgressBar(this);
        FrameLayout.LayoutParams sp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        sp.gravity = Gravity.CENTER;
        spinner.setLayoutParams(sp);

        status = new TextView(this);
        status.setTextColor(Color.WHITE);
        FrameLayout.LayoutParams tv = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        tv.gravity = Gravity.CENTER;
        tv.topMargin = 220;
        status.setLayoutParams(tv);

        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        root.addView(spinner);
        root.addView(status);
        setContentView(root);

        status.setText("Starting FinWise…");
        startBackendThenLoad();
    }

    private void startBackendThenLoad() {
        final String dataDir = getFilesDir().getAbsolutePath();
        new Thread(() -> {
            try {
                if (!Python.isStarted()) {
                    Python.start(new AndroidPlatform(this));
                }
                Python py = Python.getInstance();
                PyObject server = py.getModule("server");
                server.callAttr("init", dataDir);
                server.callAttr("start");
                runOnUiThread(() -> {
                    status.setText("Loading…");
                    webView.loadUrl("http://127.0.0.1:8000/");
                });
            } catch (final Throwable t) {
                runOnUiThread(() -> {
                    root.removeView(spinner);
                    status.setText("FinWise failed to start:\n" + t.getMessage());
                    Toast.makeText(this, "Backend error: " + t.getMessage(), Toast.LENGTH_LONG).show();
                });
            }
        }, "finwise-bootstrap").start();
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
