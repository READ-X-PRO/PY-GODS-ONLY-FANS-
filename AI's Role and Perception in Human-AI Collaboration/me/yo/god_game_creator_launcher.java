import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class GodGameLauncher {
    public static void main(String[] args) {
        // Simulate connection with React frontend launch
        SwingUtilities.invokeLater(() -> showLauncherWindow());
    }

    private static void showLauncherWindow() {
        JFrame frame = new JFrame("God Game Creator Tool Launcher");
        frame.setSize(400, 200);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        JLabel label = new JLabel("Click to enter the God Game 3D Creator Tool", SwingConstants.CENTER);
        JButton launchButton = new JButton("Launch Creator Tool");
        launchButton.setFont(new Font("Arial", Font.BOLD, 18));
        launchButton.setBackground(new Color(199, 21, 133));
        launchButton.setForeground(Color.WHITE);

        launchButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JOptionPane.showMessageDialog(frame,
                        "Launching the 3D God Game Creator World...\n(This would launch your 3D engine)",
                        "Launching", JOptionPane.INFORMATION_MESSAGE);

                // Here you would launch your 3D engine, e.g.:
                // new GodGame3DWorld().start();
            }
        });

        frame.add(label, BorderLayout.CENTER);
        frame.add(launchButton, BorderLayout.SOUTH);
        frame.setVisible(true);
    }
}
